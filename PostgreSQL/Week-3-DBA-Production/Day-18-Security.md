# Day 18: Security (Roles, Privileges, RLS, SSL)

## 📚 Learning Objectives
- Manage roles and users
- Configure granular privileges
- Implement Row-Level Security (RLS)
- Set up SSL/TLS encryption

---

## 1. Roles and Users

### Creating Roles

```sql
-- Create a user (role with LOGIN)
CREATE USER app_user WITH PASSWORD 'secure_password';

-- Create a role (group)
CREATE ROLE developer;

-- Role with options
CREATE ROLE analyst WITH
    LOGIN
    PASSWORD 'password123'
    VALID UNTIL '2025-01-01'
    CONNECTION LIMIT 10;

-- Superuser (dangerous!)
CREATE ROLE admin WITH SUPERUSER LOGIN PASSWORD 'admin_pass';

-- Role attributes
CREATE ROLE writer WITH
    CREATEDB               -- Can create databases
    CREATEROLE             -- Can create other roles
    REPLICATION            -- Can initiate replication
    BYPASSRLS              -- Bypasses row-level security
    INHERIT                -- Inherits privileges from parent roles
    LOGIN;
```

### Role Membership

```sql
-- Grant role membership
GRANT developer TO app_user;

-- User inherits developer's permissions
-- Can switch to role
SET ROLE developer;
RESET ROLE;

-- View role memberships
SELECT r.rolname, m.rolname AS member
FROM pg_roles r
JOIN pg_auth_members am ON r.oid = am.roleid
JOIN pg_roles m ON am.member = m.oid;
```

### Modify Roles

```sql
-- Change password
ALTER USER app_user WITH PASSWORD 'new_password';

-- Rename role
ALTER ROLE old_name RENAME TO new_name;

-- Add/remove attribute
ALTER ROLE app_user WITH CREATEDB;
ALTER ROLE app_user WITH NOCREATEDB;

-- Drop role (must revoke all first)
REASSIGN OWNED BY old_user TO new_user;
DROP OWNED BY old_user;
DROP ROLE old_user;
```

---

## 2. Privileges

### Object Privileges

```sql
-- Grant on tables
GRANT SELECT ON TABLE users TO reader;
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;

-- Grant on specific columns
GRANT SELECT (id, name) ON users TO limited_reader;
GRANT UPDATE (email) ON users TO user_service;

-- Grant on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Grant on functions
GRANT EXECUTE ON FUNCTION calc_total(int) TO accountant;

-- Grant on schema
GRANT USAGE ON SCHEMA analytics TO analyst;
GRANT CREATE ON SCHEMA analytics TO developer;

-- Grant on database
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT CREATE ON DATABASE mydb TO developer;
```

### Default Privileges

```sql
-- Auto-grant SELECT on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO reader;

-- Auto-grant USAGE on future sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE ON SEQUENCES TO app_user;

-- View default privileges
\ddp
```

### Revoke Privileges

```sql
-- Revoke specific permission
REVOKE INSERT ON users FROM app_user;

-- Revoke all
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM public;

-- Cascade to dependent permissions
REVOKE SELECT ON users FROM developer CASCADE;
```

### Check Privileges

```sql
-- Check table privileges
SELECT grantee, privilege_type
FROM information_schema.table_privileges
WHERE table_name = 'users';

-- Check current user's privileges
SELECT * FROM information_schema.role_table_grants
WHERE grantee = current_user;

-- Has permission?
SELECT has_table_privilege('app_user', 'users', 'SELECT');
SELECT has_schema_privilege('app_user', 'public', 'USAGE');
```

---

## 3. Row-Level Security (RLS)

### Enable RLS

```sql
-- Create multi-tenant table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    content TEXT,
    created_by INTEGER
);

-- Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Force RLS for table owner too
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
```

### Create Policies

```sql
-- Policy for tenants to see only their data
CREATE POLICY tenant_isolation ON documents
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.tenant_id')::int);

-- Usage: Set tenant context
SET app.tenant_id = '42';
SELECT * FROM documents;  -- Only sees tenant 42's documents

-- Separate read/write policies
CREATE POLICY read_own ON documents
    FOR SELECT
    USING (created_by = current_user_id());

CREATE POLICY write_own ON documents
    FOR INSERT
    WITH CHECK (created_by = current_user_id());

CREATE POLICY update_own ON documents
    FOR UPDATE
    USING (created_by = current_user_id())
    WITH CHECK (created_by = current_user_id());
```

### RLS Examples

```sql
-- Multi-level access
CREATE TABLE records (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER,
    department_id INTEGER,
    is_public BOOLEAN DEFAULT false,
    data JSONB
);

ALTER TABLE records ENABLE ROW LEVEL SECURITY;

-- Users can see: their own, their department's, or public
CREATE POLICY access_policy ON records
    FOR SELECT
    USING (
        owner_id = current_user_id()
        OR department_id = current_user_department()
        OR is_public = true
    );

-- Admins bypass RLS
CREATE POLICY admin_bypass ON records
    FOR ALL
    TO admin_role
    USING (true)
    WITH CHECK (true);
```

### View Policies

```sql
-- List all policies
SELECT * FROM pg_policies;

-- For specific table
SELECT policyname, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'documents';
```

---

## 4. Authentication (pg_hba.conf)

### Configuration File

```
# TYPE  DATABASE    USER        ADDRESS         METHOD

# Local connections
local   all         postgres                    peer
local   all         all                         md5

# IPv4 connections
host    all         all         127.0.0.1/32    scram-sha-256
host    mydb        app_user    10.0.0.0/8      scram-sha-256
host    all         all         0.0.0.0/0       reject

# IPv6 connections
host    all         all         ::1/128         scram-sha-256

# SSL required
hostssl mydb        all         0.0.0.0/0       scram-sha-256

# Replication
host    replication replicator  replica_ip/32   scram-sha-256
```

### Authentication Methods

| Method | Description |
|--------|-------------|
| `trust` | No password (dangerous!) |
| `reject` | Deny connection |
| `md5` | MD5 password hash |
| `scram-sha-256` | Strongest password method |
| `peer` | OS username must match |
| `cert` | SSL certificate |
| `ldap` | LDAP authentication |

### Reload Configuration

```bash
# Reload without restart
pg_ctl reload
# Or
SELECT pg_reload_conf();
```

---

## 5. SSL/TLS Encryption

### Generate Certificates

```bash
# Generate CA
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
    -out ca.crt -subj "/CN=PostgreSQL-CA"

# Generate server certificate
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
    -subj "/CN=db.example.com"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out server.crt -days 365

# Set permissions
chmod 600 server.key
chown postgres:postgres server.key server.crt
```

### Configure PostgreSQL

```sql
-- postgresql.conf
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
ssl_ca_file = '/path/to/ca.crt'

-- Require specific TLS version
ssl_min_protocol_version = 'TLSv1.3'

-- Strong ciphers only
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
```

### Client SSL Modes

```bash
# Connection string modes
psql "host=db.example.com sslmode=require"

# SSL modes:
# disable    - No SSL
# allow      - Try non-SSL first
# prefer     - Try SSL first (default)
# require    - Must use SSL
# verify-ca  - SSL + verify CA
# verify-full - SSL + verify CA + hostname
```

### Client Certificate Authentication

```sql
-- pg_hba.conf
hostssl mydb all 0.0.0.0/0 cert clientcert=verify-full

-- Generate client cert
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=app_user"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out client.crt -days 365
```

---

## 6. Security Best Practices

### Audit Logging

```sql
-- Enable detailed logging
log_connections = on
log_disconnections = on
log_statement = 'ddl'        -- Log DDL commands
log_duration = on
log_line_prefix = '%t [%p]: user=%u,db=%d,app=%a '

-- Or use pgAudit extension
CREATE EXTENSION pgaudit;
pgaudit.log = 'write, ddl'
```

### Security Checklist

```sql
-- 1. No default passwords
ALTER USER postgres WITH PASSWORD 'strong_random_password';

-- 2. Disable public schema access
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE mydb FROM PUBLIC;

-- 3. Use least privilege
-- Only grant what's needed

-- 4. Regular password rotation
ALTER USER app_user WITH PASSWORD 'new_password' VALID UNTIL '2024-06-01';

-- 5. Monitor superuser usage
SELECT usename, usesuper FROM pg_user WHERE usesuper;

-- 6. Check for risky settings
SELECT name, setting FROM pg_settings 
WHERE name IN ('log_connections', 'ssl', 'password_encryption');
```

---

## 📝 Key Takeaways

1. **Roles are flexible** - Can be users, groups, or both
2. **Least privilege principle** - Grant minimum required access
3. **RLS for multi-tenancy** - Database-enforced data isolation
4. **Always use SSL** - Encrypt data in transit
5. **pg_hba.conf is critical** - First line of defense

---

## ✅ Day 18 Checklist

- [ ] Create roles and users
- [ ] Configure granular privileges
- [ ] Implement RLS policies
- [ ] Set up SSL/TLS
- [ ] Configure pg_hba.conf
- [ ] Enable audit logging
