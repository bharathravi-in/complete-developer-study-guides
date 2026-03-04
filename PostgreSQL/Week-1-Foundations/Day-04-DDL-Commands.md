# Day 4: DDL Commands

## 📚 Learning Objectives
- Master CREATE, ALTER, DROP statements
- Deep dive into constraints
- Understand DEFERRABLE constraints
- Learn best practices for schema management

---

## 1. CREATE Statements

### CREATE TABLE

```sql
-- Basic table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Full syntax with all options
CREATE TABLE IF NOT EXISTS orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE DEFAULT CURRENT_DATE,
    total NUMERIC(12,2) CHECK (total >= 0),
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(id) ON DELETE CASCADE
) TABLESPACE fast_storage;

-- Create table from query
CREATE TABLE active_users AS
SELECT * FROM users WHERE status = 'active';

-- Create table with same structure (no data)
CREATE TABLE users_backup (LIKE users INCLUDING ALL);

-- Including options
CREATE TABLE users_copy (
    LIKE users 
    INCLUDING DEFAULTS 
    INCLUDING CONSTRAINTS 
    INCLUDING INDEXES 
    INCLUDING COMMENTS
);
```

### CREATE INDEX

```sql
-- Basic index
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- Multi-column index
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- Partial index (index only subset of rows)
CREATE INDEX idx_active_users ON users(email) 
WHERE status = 'active';

-- Expression index
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Concurrent index (doesn't lock table)
CREATE INDEX CONCURRENTLY idx_large_table_col ON large_table(column);

-- Index types
CREATE INDEX idx_gin_tags ON posts USING GIN(tags);
CREATE INDEX idx_gist_location ON places USING GIST(location);
CREATE INDEX idx_brin_created ON logs USING BRIN(created_at);
```

### CREATE VIEW

```sql
-- Basic view
CREATE VIEW active_employees AS
SELECT id, name, email 
FROM employees 
WHERE status = 'active';

-- View with column aliases
CREATE VIEW employee_summary (emp_id, full_name, dept) AS
SELECT e.id, e.first_name || ' ' || e.last_name, d.name
FROM employees e
JOIN departments d ON e.dept_id = d.id;

-- Replace existing view
CREATE OR REPLACE VIEW active_employees AS
SELECT id, name, email, department_id
FROM employees 
WHERE status = 'active';

-- Materialized view (cached query results)
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    SUM(total) AS revenue,
    COUNT(*) AS order_count
FROM orders
GROUP BY DATE_TRUNC('month', order_date);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW monthly_sales;
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales;  -- Requires unique index
```

### CREATE SEQUENCE

```sql
-- Basic sequence
CREATE SEQUENCE order_id_seq;

-- Full options
CREATE SEQUENCE invoice_number_seq
    START WITH 1000
    INCREMENT BY 1
    MINVALUE 1000
    MAXVALUE 9999999
    CYCLE
    CACHE 10;

-- Use sequence
SELECT nextval('invoice_number_seq');
SELECT currval('invoice_number_seq');
SELECT setval('invoice_number_seq', 5000);  -- Set to specific value

-- Associate with column
ALTER SEQUENCE order_id_seq OWNED BY orders.order_id;
```

---

## 2. ALTER Statements

### ALTER TABLE - Columns

```sql
-- Add column
ALTER TABLE employees ADD COLUMN phone VARCHAR(20);

-- Add column with default
ALTER TABLE employees 
ADD COLUMN is_active BOOLEAN DEFAULT true NOT NULL;

-- Drop column
ALTER TABLE employees DROP COLUMN phone;

-- Rename column
ALTER TABLE employees RENAME COLUMN name TO full_name;

-- Change data type
ALTER TABLE employees 
ALTER COLUMN phone TYPE VARCHAR(30);

-- Change type with conversion
ALTER TABLE employees 
ALTER COLUMN age TYPE VARCHAR(3) USING age::VARCHAR;

-- Set/Drop default
ALTER TABLE employees ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE employees ALTER COLUMN status DROP DEFAULT;

-- Set/Drop NOT NULL
ALTER TABLE employees ALTER COLUMN email SET NOT NULL;
ALTER TABLE employees ALTER COLUMN phone DROP NOT NULL;
```

### ALTER TABLE - Constraints

```sql
-- Add constraint
ALTER TABLE employees 
ADD CONSTRAINT uq_email UNIQUE (email);

ALTER TABLE employees 
ADD CONSTRAINT chk_salary CHECK (salary > 0);

ALTER TABLE orders 
ADD CONSTRAINT fk_customer 
FOREIGN KEY (customer_id) REFERENCES customers(id);

-- Drop constraint
ALTER TABLE employees DROP CONSTRAINT uq_email;

-- Rename constraint
ALTER TABLE employees 
RENAME CONSTRAINT chk_salary TO chk_positive_salary;

-- Validate constraint without blocking
ALTER TABLE orders 
ADD CONSTRAINT fk_customer 
FOREIGN KEY (customer_id) REFERENCES customers(id) 
NOT VALID;  -- Doesn't check existing rows

ALTER TABLE orders VALIDATE CONSTRAINT fk_customer;  -- Validate later
```

### ALTER TABLE - Table Level

```sql
-- Rename table
ALTER TABLE employees RENAME TO staff;

-- Change owner
ALTER TABLE employees OWNER TO hr_admin;

-- Change schema
ALTER TABLE employees SET SCHEMA hr;

-- Change tablespace
ALTER TABLE employees SET TABLESPACE fast_storage;

-- Enable/disable triggers
ALTER TABLE employees DISABLE TRIGGER trigger_name;
ALTER TABLE employees ENABLE TRIGGER trigger_name;
ALTER TABLE employees DISABLE TRIGGER ALL;

-- Set/reset storage parameters
ALTER TABLE employees SET (fillfactor = 80);
ALTER TABLE employees RESET (fillfactor);
```

### ALTER SEQUENCE / INDEX / VIEW

```sql
-- Alter sequence
ALTER SEQUENCE order_seq RESTART WITH 1000;
ALTER SEQUENCE order_seq INCREMENT BY 10;

-- Alter index
ALTER INDEX idx_users_email RENAME TO idx_users_email_new;
ALTER INDEX idx_users_email SET TABLESPACE fast_storage;

-- Alter view
ALTER VIEW active_users RENAME TO current_users;
ALTER VIEW active_users OWNER TO admin;
```

---

## 3. DROP Statements

```sql
-- Drop table
DROP TABLE employees;
DROP TABLE IF EXISTS employees;
DROP TABLE employees CASCADE;  -- Drop dependent objects

-- Drop multiple tables
DROP TABLE table1, table2, table3;

-- Drop index
DROP INDEX idx_users_email;
DROP INDEX CONCURRENTLY idx_users_email;  -- Non-blocking

-- Drop view
DROP VIEW active_users;
DROP VIEW active_users CASCADE;

-- Drop materialized view
DROP MATERIALIZED VIEW monthly_sales;

-- Drop sequence
DROP SEQUENCE order_seq;

-- Drop schema
DROP SCHEMA hr;
DROP SCHEMA hr CASCADE;

-- Drop type
DROP TYPE status_type;
DROP TYPE status_type CASCADE;
```

---

## 4. Constraints Deep Dive

### PRIMARY KEY

```sql
-- Single column
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255)
);

-- Composite primary key
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);

-- Named primary key
CREATE TABLE products (
    id INT,
    CONSTRAINT pk_products PRIMARY KEY (id)
);
```

### FOREIGN KEY

```sql
-- Basic foreign key
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id)
);

-- Full options
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT,
    salesperson_id INT,
    CONSTRAINT fk_customer 
        FOREIGN KEY (customer_id) 
        REFERENCES customers(id) 
        ON DELETE CASCADE
        ON UPDATE SET NULL,
    CONSTRAINT fk_salesperson 
        FOREIGN KEY (salesperson_id) 
        REFERENCES employees(id) 
        ON DELETE SET NULL
);
```

#### Referential Actions

| Action | ON DELETE | ON UPDATE |
|--------|-----------|-----------|
| `NO ACTION` | Error (default) | Error (default) |
| `RESTRICT` | Error (immediate) | Error (immediate) |
| `CASCADE` | Delete child rows | Update child rows |
| `SET NULL` | Set FK to NULL | Set FK to NULL |
| `SET DEFAULT` | Set FK to default | Set FK to default |

```sql
-- Self-referencing foreign key
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    parent_id INT REFERENCES categories(id) ON DELETE CASCADE
);
```

### UNIQUE Constraint

```sql
-- Column level
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE
);

-- Table level (composite)
CREATE TABLE user_roles (
    user_id INT,
    role_id INT,
    UNIQUE (user_id, role_id)
);

-- Named constraint
CREATE TABLE products (
    sku VARCHAR(50),
    CONSTRAINT uq_products_sku UNIQUE (sku)
);

-- Partial unique (only unique within subset)
CREATE UNIQUE INDEX uq_active_email ON users(email) 
WHERE status = 'active';

-- NULL handling: Multiple NULLs allowed in UNIQUE columns
INSERT INTO users (email) VALUES (NULL), (NULL);  -- Both allowed
```

### CHECK Constraint

```sql
-- Column level
CREATE TABLE products (
    price NUMERIC CHECK (price > 0),
    quantity INT CHECK (quantity >= 0)
);

-- Table level (can reference multiple columns)
CREATE TABLE orders (
    start_date DATE,
    end_date DATE,
    discount NUMERIC(5,2),
    CHECK (end_date >= start_date),
    CHECK (discount BETWEEN 0 AND 100)
);

-- Named constraint
CREATE TABLE employees (
    salary NUMERIC,
    CONSTRAINT chk_positive_salary CHECK (salary > 0)
);

-- Complex checks
CREATE TABLE events (
    event_type VARCHAR(20),
    capacity INT,
    CONSTRAINT chk_capacity CHECK (
        (event_type = 'small' AND capacity <= 50) OR
        (event_type = 'medium' AND capacity BETWEEN 51 AND 200) OR
        (event_type = 'large' AND capacity > 200)
    )
);
```

### NOT NULL Constraint

```sql
-- Column level
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL
);

-- Adding to existing column
ALTER TABLE users ALTER COLUMN name SET NOT NULL;

-- Dropping
ALTER TABLE users ALTER COLUMN name DROP NOT NULL;

-- Best practice: Add NOT NULL with default
ALTER TABLE users 
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active';
```

### DEFAULT Constraint

```sql
-- Simple defaults
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    status VARCHAR(20) DEFAULT 'draft',
    view_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Expression defaults
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid(),
    code VARCHAR(10) DEFAULT 'USR' || nextval('user_code_seq')::TEXT
);

-- Generated columns (computed)
CREATE TABLE products (
    price NUMERIC,
    tax_rate NUMERIC DEFAULT 0.1,
    total NUMERIC GENERATED ALWAYS AS (price * (1 + tax_rate)) STORED
);
```

---

## 5. DEFERRABLE Constraints

### Why Deferrable?

Deferrable constraints allow you to temporarily violate constraints during a transaction, as long as they're satisfied when the transaction commits.

**Use Cases:**
- Circular foreign keys
- Bulk data loading
- Complex multi-row updates

### Constraint Timing

| Type | When Checked |
|------|-------------|
| `NOT DEFERRABLE` | After each statement (default) |
| `DEFERRABLE INITIALLY IMMEDIATE` | After each statement, but can be deferred |
| `DEFERRABLE INITIALLY DEFERRED` | At transaction commit |

### Examples

```sql
-- Circular foreign keys problem
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT
);

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    head_id INT REFERENCES employees(id)  -- Employee runs department
);

-- Now add FK from employees to departments
ALTER TABLE employees 
ADD CONSTRAINT fk_manager 
FOREIGN KEY (manager_id) REFERENCES employees(id);

-- This fails! Can't insert both at same time
INSERT INTO departments (name, head_id) VALUES ('Engineering', 1);
INSERT INTO employees (name, manager_id) VALUES ('John', NULL);

-- Solution: Deferrable constraints
CREATE TABLE employees_v2 (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department_id INT
);

CREATE TABLE departments_v2 (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    head_id INT,
    CONSTRAINT fk_head FOREIGN KEY (head_id) 
        REFERENCES employees_v2(id) 
        DEFERRABLE INITIALLY DEFERRED
);

ALTER TABLE employees_v2 
ADD CONSTRAINT fk_dept 
FOREIGN KEY (department_id) 
REFERENCES departments_v2(id) 
DEFERRABLE INITIALLY DEFERRED;

-- Now this works!
BEGIN;
INSERT INTO employees_v2 (id, name, department_id) VALUES (1, 'John', 1);
INSERT INTO departments_v2 (id, name, head_id) VALUES (1, 'Engineering', 1);
COMMIT;  -- Constraints checked here
```

### Controlling Deferral

```sql
-- Set constraint mode for session
SET CONSTRAINTS ALL DEFERRED;
SET CONSTRAINTS ALL IMMEDIATE;

-- Set specific constraint
SET CONSTRAINTS fk_manager DEFERRED;

-- Within transaction
BEGIN;
SET CONSTRAINTS fk_manager DEFERRED;
-- ... operations ...
COMMIT;  -- Constraints checked
```

---

## 6. TRUNCATE vs DELETE

```sql
-- DELETE: Row-by-row, logged, triggers fire
DELETE FROM large_table;

-- TRUNCATE: Fast, minimal logging, no triggers
TRUNCATE TABLE large_table;

-- TRUNCATE options
TRUNCATE TABLE large_table RESTART IDENTITY;  -- Reset sequences
TRUNCATE TABLE large_table CASCADE;           -- Truncate dependent tables
TRUNCATE TABLE t1, t2, t3;                    -- Multiple tables

-- TRUNCATE is not MVCC-safe (no rollback in some scenarios)
-- Use DELETE for transactional safety
```

---

## 7. Best Practices

### Schema Design

```sql
-- ✅ Good: Explicit constraints, clear names
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total NUMERIC(12,2) NOT NULL CHECK (total >= 0),
    
    CONSTRAINT fk_orders_customer 
        FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id)
        ON DELETE RESTRICT,
    CONSTRAINT chk_orders_status 
        CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled'))
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status) WHERE status != 'delivered';
```

### Migration Safety

```sql
-- Adding column (safe)
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- Adding NOT NULL column (requires default for existing rows)
ALTER TABLE users 
ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT false;

-- Adding index (use CONCURRENTLY in production)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Changing column type (may lock table)
-- Better: Create new column, backfill, swap
ALTER TABLE users ADD COLUMN phone_new VARCHAR(30);
UPDATE users SET phone_new = phone;
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users RENAME COLUMN phone_new TO phone;
```

---

## 🔬 Hands-On Practice

```sql
-- Create complete schema
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INT REFERENCES categories(category_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL,
    cost NUMERIC(10,2),
    category_id INT NOT NULL REFERENCES categories(category_id),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    attributes JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT uq_products_sku UNIQUE (sku),
    CONSTRAINT chk_products_price CHECK (price > 0),
    CONSTRAINT chk_products_cost CHECK (cost IS NULL OR cost > 0),
    CONSTRAINT chk_products_margin CHECK (cost IS NULL OR price >= cost),
    CONSTRAINT chk_products_status CHECK (status IN ('active', 'inactive', 'discontinued'))
);

-- Indexes
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_status ON products(status) WHERE status = 'active';
CREATE INDEX idx_products_tags ON products USING GIN(tags);
CREATE INDEX idx_products_attributes ON products USING GIN(attributes);
```

---

## 📝 Key Takeaways

1. **Use IF EXISTS / IF NOT EXISTS** - Safer migrations
2. **Name your constraints** - Easier to modify later
3. **Use CONCURRENTLY for production indexes** - Avoids locking
4. **DEFERRABLE for circular references** - Solves chicken-egg problems
5. **Consider partial indexes** - Index only relevant rows
6. **TRUNCATE for fast deletion** - But be aware of MVCC implications

---

## ✅ Day 4 Checklist

- [ ] Create tables with all constraint types
- [ ] Practice ALTER TABLE operations
- [ ] Create indexes (B-tree, GIN)
- [ ] Understand CASCADE behavior
- [ ] Use DEFERRABLE constraints
- [ ] Practice safe migration patterns
