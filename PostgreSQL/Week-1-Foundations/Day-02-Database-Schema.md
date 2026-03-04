# Day 2: Database & Schema Deep Dive

## 📚 Learning Objectives
- Understand database vs schema concepts
- Learn about tablespaces
- Master system catalogs
- Understand search_path
- Apply naming conventions

---

## 1. Databases vs Schemas

### Conceptual Hierarchy

```
PostgreSQL Cluster (Instance)
├── Database 1
│   ├── Schema: public
│   │   ├── Table A
│   │   └── Table B
│   ├── Schema: sales
│   │   ├── Table C
│   │   └── Table D
│   └── Schema: hr
│       └── Table E
├── Database 2
│   ├── Schema: public
│   └── Schema: analytics
└── Database 3
```

### Key Differences

| Feature | Database | Schema |
|---------|----------|--------|
| Isolation | Complete | Namespace only |
| Cross-query | ❌ Cannot join | ✅ Can join |
| Connections | Separate per DB | Same connection |
| Users | Can be isolated | Shared within DB |
| Size | Own data directory | Within database |

### When to Use What?

**Use Databases for:**
- Completely separate applications
- Different security requirements
- Different encoding/collation needs
- Multi-tenant isolation (strong)

**Use Schemas for:**
- Organizing related objects
- Same application modules
- Multi-tenant (soft isolation)
- Version control of structures

---

## 2. Database Management

### Creating Databases

```sql
-- Basic creation
CREATE DATABASE company;

-- Full syntax
CREATE DATABASE company
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = false;

-- Create from template
CREATE DATABASE company_test 
    TEMPLATE company;
```

### Template Databases

```sql
-- View templates
SELECT datname, datistemplate, datallowconn 
FROM pg_database;
```

| Template | Description |
|----------|-------------|
| `template0` | Pristine, never modified |
| `template1` | Default template, can be customized |

```sql
-- Create clean database (useful for encoding issues)
CREATE DATABASE mydb TEMPLATE template0 ENCODING 'UTF8';
```

### Database Operations

```sql
-- List databases
\l
-- or
SELECT datname, pg_size_pretty(pg_database_size(datname)) as size 
FROM pg_database ORDER BY pg_database_size(datname) DESC;

-- Connect to database
\c company
-- or
\connect company

-- Rename database (no active connections)
ALTER DATABASE company RENAME TO company_prod;

-- Change owner
ALTER DATABASE company OWNER TO admin;

-- Set configuration
ALTER DATABASE company SET timezone TO 'UTC';

-- Drop database
DROP DATABASE company;
-- Force drop (terminate connections) - PostgreSQL 13+
DROP DATABASE company WITH (FORCE);
```

---

## 3. Schema Management

### Default Schema

Every database has a `public` schema by default.

```sql
-- Current schema
SELECT current_schema();

-- All schemas
SELECT schema_name FROM information_schema.schemata;
-- or
\dn
```

### Creating Schemas

```sql
-- Basic creation
CREATE SCHEMA hr;

-- With owner
CREATE SCHEMA sales AUTHORIZATION sales_admin;

-- With objects
CREATE SCHEMA inventory
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100)
    )
    CREATE VIEW active_products AS 
        SELECT * FROM products WHERE active = true;

-- If not exists
CREATE SCHEMA IF NOT EXISTS analytics;
```

### Schema Operations

```sql
-- Rename schema
ALTER SCHEMA hr RENAME TO human_resources;

-- Change owner
ALTER SCHEMA hr OWNER TO hr_admin;

-- Drop schema
DROP SCHEMA hr;

-- Drop with all objects (CASCADE)
DROP SCHEMA hr CASCADE;
```

### Working with Schemas

```sql
-- Create table in specific schema
CREATE TABLE hr.employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department_id INT
);

-- Access table with schema prefix
SELECT * FROM hr.employees;

-- Set search_path to avoid prefixing
SET search_path TO hr, public;
SELECT * FROM employees;  -- Now works without prefix
```

---

## 4. search_path

### Understanding search_path

```sql
-- View current search_path
SHOW search_path;
-- Default output: "$user", public

-- What happens during object lookup:
-- 1. First check schema matching username
-- 2. Then check public schema
-- 3. Object not found error if missing
```

### Setting search_path

```sql
-- Session level
SET search_path TO sales, hr, public;

-- Permanent for user
ALTER ROLE sales_user SET search_path TO sales, public;

-- Permanent for database
ALTER DATABASE company SET search_path TO company, public;

-- In function definition
CREATE FUNCTION get_employees() 
RETURNS TABLE(id INT, name VARCHAR)
LANGUAGE SQL
SET search_path TO hr, public
AS $$
    SELECT id, name FROM employees;
$$;
```

### search_path Security

```sql
-- Recommended for functions (avoid search_path attacks)
CREATE FUNCTION secure_function()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, pg_temp
AS $$
BEGIN
    -- Use fully qualified names inside
    PERFORM * FROM public.users;
END;
$$;
```

---

## 5. Tablespaces

### What are Tablespaces?

Tablespaces allow you to define locations on disk where PostgreSQL stores database files.

### Use Cases
- Distribute I/O across multiple disks
- Place frequently accessed data on fast SSD
- Archive old data on slower storage
- Manage disk space allocation

### Creating Tablespaces

```bash
# First, create directory (as postgres user)
sudo mkdir -p /mnt/ssd/postgresql
sudo chown postgres:postgres /mnt/ssd/postgresql
```

```sql
-- Create tablespace
CREATE TABLESPACE fast_storage 
    LOCATION '/mnt/ssd/postgresql';

-- With options
CREATE TABLESPACE fast_storage 
    OWNER admin
    LOCATION '/mnt/ssd/postgresql';
```

### Using Tablespaces

```sql
-- Create database in tablespace
CREATE DATABASE analytics TABLESPACE fast_storage;

-- Create table in tablespace
CREATE TABLE large_data (
    id SERIAL,
    data JSONB
) TABLESPACE fast_storage;

-- Create index in tablespace
CREATE INDEX idx_large_data 
    ON large_data(id) 
    TABLESPACE fast_storage;

-- Move table to different tablespace
ALTER TABLE large_data SET TABLESPACE slow_storage;

-- Set default tablespace
SET default_tablespace = fast_storage;
ALTER DATABASE mydb SET default_tablespace = fast_storage;
```

### Managing Tablespaces

```sql
-- List tablespaces
\db
-- or
SELECT spcname, pg_size_pretty(pg_tablespace_size(spcname)) 
FROM pg_tablespace;

-- View tablespace location
SELECT spcname, pg_tablespace_location(oid) 
FROM pg_tablespace;

-- Drop tablespace (must be empty)
DROP TABLESPACE fast_storage;
```

---

## 6. System Catalogs Deep Dive

### Catalog Structure

```
pg_catalog (schema)
├── pg_class        -- Tables, indexes, sequences, views
├── pg_namespace    -- Schemas
├── pg_attribute    -- Columns
├── pg_type         -- Data types
├── pg_index        -- Index information
├── pg_constraint   -- Constraints
├── pg_proc         -- Functions/procedures
├── pg_trigger      -- Triggers
├── pg_roles        -- Roles (users/groups)
├── pg_database     -- Databases
└── ... many more
```

### Essential Catalog Queries

```sql
-- All tables with details
SELECT 
    n.nspname AS schema,
    c.relname AS table_name,
    c.relkind AS type,
    pg_size_pretty(pg_relation_size(c.oid)) AS size,
    c.reltuples::bigint AS approx_rows
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'  -- 'r' = regular table
AND n.nspname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(c.oid) DESC;

-- Column information
SELECT 
    a.attname AS column_name,
    t.typname AS data_type,
    a.attnotnull AS not_null,
    a.atthasdef AS has_default
FROM pg_attribute a
JOIN pg_class c ON c.oid = a.attrelid
JOIN pg_type t ON t.oid = a.atttypid
WHERE c.relname = 'employees'
AND a.attnum > 0
AND NOT a.attisdropped;

-- Constraints
SELECT 
    conname AS constraint_name,
    contype AS type,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid = 'employees'::regclass;

-- Indexes
SELECT 
    i.relname AS index_name,
    am.amname AS type,
    pg_get_indexdef(i.oid) AS definition
FROM pg_index x
JOIN pg_class i ON i.oid = x.indexrelid
JOIN pg_am am ON am.oid = i.relam
WHERE x.indrelid = 'employees'::regclass;
```

### information_schema Queries

```sql
-- Tables
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema');

-- Columns
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'employees';

-- Constraints
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'employees';
```

---

## 7. Naming Conventions

### Best Practices

| Object | Convention | Example |
|--------|------------|---------|
| Tables | snake_case, plural | `user_accounts` |
| Columns | snake_case | `created_at` |
| Primary Key | `id` or `table_id` | `user_id` |
| Foreign Key | `referenced_table_id` | `department_id` |
| Indexes | `idx_table_column` | `idx_users_email` |
| Unique | `uq_table_column` | `uq_users_email` |
| Check | `chk_table_condition` | `chk_users_age` |
| Foreign Key Constraint | `fk_table_reference` | `fk_users_department` |
| Functions | `verb_noun` | `get_user_by_id` |
| Triggers | `trg_table_timing_event` | `trg_users_before_insert` |
| Sequences | `table_column_seq` | `users_id_seq` |

### Examples

```sql
-- Well-named table
CREATE TABLE user_accounts (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    department_id INT REFERENCES departments(department_id),
    CONSTRAINT uq_user_accounts_email UNIQUE (email),
    CONSTRAINT chk_user_accounts_email CHECK (email ~* '^.+@.+\..+$')
);

-- Well-named index
CREATE INDEX idx_user_accounts_created_at ON user_accounts(created_at);

-- Well-named function
CREATE FUNCTION get_user_by_email(p_email VARCHAR)
RETURNS user_accounts AS $$
    SELECT * FROM user_accounts WHERE email = p_email;
$$ LANGUAGE SQL;
```

### Avoid These

```sql
-- ❌ Bad naming
CREATE TABLE Users (
    ID INT,
    Email VARCHAR(100),
    "Created At" TIMESTAMP,  -- Requires quotes everywhere
    dept INT  -- Ambiguous abbreviation
);

-- ✅ Good naming
CREATE TABLE users (
    user_id INT,
    email VARCHAR(100),
    created_at TIMESTAMP,
    department_id INT
);
```

---

## 🔬 Hands-On Practice

### Create Company Structure

```sql
-- Create database
CREATE DATABASE company;
\c company

-- Create schemas
CREATE SCHEMA hr;
CREATE SCHEMA sales;
CREATE SCHEMA inventory;

-- Set search_path
SET search_path TO public, hr, sales;

-- Create tables in schemas
CREATE TABLE hr.departments (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hr.employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department_id INT REFERENCES hr.departments(department_id),
    hire_date DATE DEFAULT CURRENT_DATE,
    salary NUMERIC(10,2)
);

CREATE TABLE sales.customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES sales.customers(customer_id),
    employee_id INT REFERENCES hr.employees(employee_id),
    order_date DATE DEFAULT CURRENT_DATE,
    total NUMERIC(12,2)
);

-- Verify structure
\dn                    -- List schemas
\dt hr.*               -- List tables in hr schema
\dt sales.*            -- List tables in sales schema
\d hr.employees        -- Describe table
```

### Explore Cross-Schema Queries

```sql
-- Insert test data
INSERT INTO hr.departments (name) VALUES ('Engineering'), ('Sales'), ('HR');
INSERT INTO hr.employees (first_name, last_name, email, department_id, salary)
VALUES 
    ('John', 'Doe', 'john@company.com', 1, 75000),
    ('Jane', 'Smith', 'jane@company.com', 2, 65000);

INSERT INTO sales.customers (name, email) 
VALUES ('Acme Corp', 'contact@acme.com');

INSERT INTO sales.orders (customer_id, employee_id, total)
VALUES (1, 2, 5000.00);

-- Cross-schema join
SELECT 
    o.order_id,
    c.name AS customer,
    e.first_name || ' ' || e.last_name AS sales_rep,
    o.total
FROM sales.orders o
JOIN sales.customers c ON c.customer_id = o.customer_id
JOIN hr.employees e ON e.employee_id = o.employee_id;
```

---

## 📝 Key Takeaways

1. **Databases provide complete isolation** - Cannot join across databases
2. **Schemas are namespaces** - Objects in same database can be joined
3. **search_path controls lookup order** - Important for security and convenience
4. **Tablespaces manage storage location** - Useful for performance optimization
5. **System catalogs are queryable** - pg_catalog and information_schema
6. **Consistent naming is crucial** - Use snake_case, be descriptive

---

## ✅ Day 2 Checklist

- [ ] Create a new database
- [ ] Create multiple schemas
- [ ] Understand search_path
- [ ] Query system catalogs
- [ ] Practice naming conventions
- [ ] Create cross-schema structures
