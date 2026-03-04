# Day 26: Extensions (PostGIS, pg_cron, pg_stat_statements, etc.)

## 📚 Learning Objectives
- Understand PostgreSQL extension system
- Master essential extensions
- Configure and use popular extensions
- Build production-ready setups

---

## 1. Extension Basics

### Managing Extensions

```sql
-- List available extensions
SELECT * FROM pg_available_extensions ORDER BY name;

-- List installed extensions
SELECT * FROM pg_extension;

-- Install extension
CREATE EXTENSION IF NOT EXISTS extension_name;

-- Install with specific schema
CREATE EXTENSION pg_trgm SCHEMA public;

-- Upgrade extension
ALTER EXTENSION extension_name UPDATE;

-- Remove extension
DROP EXTENSION extension_name;
DROP EXTENSION extension_name CASCADE;  -- Drop dependent objects
```

### Extension Search Path

```sql
-- Extensions are loaded from:
SHOW shared_preload_libraries;  -- Loaded at server start

-- For some extensions:
-- 1. Add to shared_preload_libraries in postgresql.conf
-- 2. Restart PostgreSQL
-- 3. CREATE EXTENSION
```

---

## 2. pg_stat_statements (Query Analysis)

### Setup

```sql
-- postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all  -- top, none, all
pg_stat_statements.max = 10000

-- Restart PostgreSQL, then:
CREATE EXTENSION pg_stat_statements;
```

### Usage

```sql
-- Top queries by total time
SELECT 
    LEFT(query, 80) AS query,
    calls,
    ROUND(total_exec_time::numeric, 2) AS total_ms,
    ROUND(mean_exec_time::numeric, 2) AS avg_ms,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Queries with worst cache hit ratio
SELECT 
    LEFT(query, 60) AS query,
    calls,
    shared_blks_hit,
    shared_blks_read,
    ROUND(100.0 * shared_blks_hit / 
        NULLIF(shared_blks_hit + shared_blks_read, 0), 2) AS hit_ratio
FROM pg_stat_statements
WHERE shared_blks_read > 0
ORDER BY hit_ratio ASC
LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

---

## 3. pg_trgm (Fuzzy Text Search)

### Setup

```sql
CREATE EXTENSION pg_trgm;
```

### Similarity Search

```sql
-- Trigram similarity (0-1, higher = more similar)
SELECT similarity('hello', 'helo');
-- Result: 0.5

SELECT similarity('postgresql', 'postgres');
-- Result: 0.6

-- Find similar strings
SELECT name, similarity(name, 'Jon Smith')
FROM users
WHERE similarity(name, 'Jon Smith') > 0.3
ORDER BY similarity(name, 'Jon Smith') DESC;

-- % operator (similarity threshold, default 0.3)
SELECT * FROM users WHERE name % 'Jon Smith';

-- Change threshold
SET pg_trgm.similarity_threshold = 0.5;
```

### LIKE/ILIKE Index Support

```sql
-- Create GIN index for trigrams
CREATE INDEX idx_users_name_trgm ON users USING GIN (name gin_trgm_ops);

-- Now LIKE with leading wildcard uses index!
SELECT * FROM users WHERE name LIKE '%smith%';  -- Uses index!
SELECT * FROM users WHERE name ILIKE '%smith%'; -- Uses index!

-- GiST for similarity
CREATE INDEX idx_users_name_gist ON users USING GIST (name gist_trgm_ops);

-- Supports % operator and ORDER BY similarity
SELECT * FROM users 
WHERE name % 'Jon Smith'
ORDER BY name <-> 'Jon Smith';  -- Distance operator (1 - similarity)
```

---

## 4. PostGIS (Geospatial)

### Setup

```sql
CREATE EXTENSION postgis;
```

### Basic Types

```sql
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location GEOMETRY(Point, 4326)  -- SRID 4326 = WGS84 (GPS)
);

-- Insert point (longitude, latitude)
INSERT INTO locations (name, location) VALUES
('New York', ST_SetSRID(ST_MakePoint(-74.0060, 40.7128), 4326)),
('London', ST_SetSRID(ST_MakePoint(-0.1276, 51.5074), 4326));

-- Or using WKT (Well-Known Text)
INSERT INTO locations (name, location) VALUES
('Paris', ST_GeomFromText('POINT(2.3522 48.8566)', 4326));
```

### Common Operations

```sql
-- Distance between points (meters)
SELECT ST_Distance(
    ST_Transform(a.location, 3857),  -- Transform to meters
    ST_Transform(b.location, 3857)
)
FROM locations a, locations b
WHERE a.name = 'New York' AND b.name = 'London';

-- Distance using geography type (accurate for large distances)
SELECT ST_Distance(
    a.location::geography,
    b.location::geography
) / 1000 AS km  -- Convert to km
FROM locations a, locations b
WHERE a.name = 'New York' AND b.name = 'London';

-- Find locations within 10km
SELECT name FROM locations
WHERE ST_DWithin(
    location::geography,
    ST_SetSRID(ST_MakePoint(-74.0060, 40.7128), 4326)::geography,
    10000  -- 10km in meters
);

-- Point in polygon
SELECT name FROM locations
WHERE ST_Within(
    location,
    ST_SetSRID(ST_MakePolygon(ST_GeomFromText(
        'LINESTRING(-75 40, -73 40, -73 42, -75 42, -75 40)'
    )), 4326)
);
```

### Spatial Index

```sql
-- GiST index for geometry
CREATE INDEX idx_locations_geom ON locations USING GIST (location);

-- Use with spatial queries
EXPLAIN SELECT * FROM locations
WHERE ST_DWithin(location::geography, ..., 10000);
```

---

## 5. pg_cron (Scheduled Jobs)

### Setup

```sql
-- postgresql.conf
shared_preload_libraries = 'pg_cron'
cron.database_name = 'mydb'

-- Restart PostgreSQL
CREATE EXTENSION pg_cron;
```

### Schedule Jobs

```sql
-- Run VACUUM every day at 3 AM
SELECT cron.schedule('vacuum-job', '0 3 * * *', 
    'VACUUM ANALYZE users');

-- Run every 5 minutes
SELECT cron.schedule('refresh-cache', '*/5 * * * *',
    'CALL refresh_materialized_views()');

-- Run weekly on Sunday
SELECT cron.schedule('weekly-cleanup', '0 0 * * 0',
    'DELETE FROM logs WHERE created_at < now() - interval ''30 days''');

-- Cron format: minute hour day month weekday
-- * * * * * = every minute
-- 0 * * * * = every hour
-- 0 0 * * * = daily at midnight
-- 0 0 * * 0 = weekly on Sunday
```

### Manage Jobs

```sql
-- List all jobs
SELECT * FROM cron.job;

-- View job run history
SELECT * FROM cron.job_run_details 
ORDER BY start_time DESC 
LIMIT 20;

-- Unschedule job
SELECT cron.unschedule('vacuum-job');

-- Or by job id
SELECT cron.unschedule(jobid) FROM cron.job WHERE jobname = 'vacuum-job';
```

---

## 6. uuid-ossp / pgcrypto

### UUID Generation

```sql
-- uuid-ossp extension
CREATE EXTENSION "uuid-ossp";

SELECT uuid_generate_v4();  -- Random UUID
SELECT uuid_generate_v1();  -- Time-based

-- pgcrypto (also has UUID)
CREATE EXTENSION pgcrypto;

SELECT gen_random_uuid();  -- Preferred in PG 13+

-- In table
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100)
);
```

### Encryption with pgcrypto

```sql
-- Hash password
SELECT crypt('mypassword', gen_salt('bf'));
-- Result: $2a$06$... (bcrypt hash)

-- Verify password
SELECT crypt('mypassword', stored_hash) = stored_hash;

-- Symmetric encryption
SELECT pgp_sym_encrypt('secret data', 'encryption_key');
SELECT pgp_sym_decrypt(encrypted_data, 'encryption_key');

-- Hash functions
SELECT digest('hello', 'sha256');
SELECT encode(digest('hello', 'sha256'), 'hex');
```

---

## 7. Other Useful Extensions

### hstore (Key-Value)

```sql
CREATE EXTENSION hstore;

CREATE TABLE configs (
    id SERIAL PRIMARY KEY,
    settings HSTORE
);

INSERT INTO configs (settings) VALUES (
    'timeout => 30, retries => 3, debug => false'
);

SELECT settings -> 'timeout' FROM configs;
SELECT settings ? 'timeout' FROM configs;  -- Key exists?
```

### ltree (Label Tree)

```sql
CREATE EXTENSION ltree;

-- Hierarchical paths
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    path LTREE
);

INSERT INTO categories (path) VALUES
('root'),
('root.electronics'),
('root.electronics.phones'),
('root.electronics.laptops'),
('root.clothing');

-- Find all under electronics
SELECT * FROM categories WHERE path <@ 'root.electronics';

-- Find direct children
SELECT * FROM categories WHERE path ~ 'root.*{1}';
```

### tablefunc (Crosstab/Pivot)

```sql
CREATE EXTENSION tablefunc;

-- Pivot data
SELECT * FROM crosstab(
    'SELECT department, quarter, revenue 
     FROM sales ORDER BY 1, 2'
) AS ct(department TEXT, q1 NUMERIC, q2 NUMERIC, q3 NUMERIC, q4 NUMERIC);
```

---

## 8. Extension Best Practices

```sql
-- 1. Install in dedicated schema
CREATE SCHEMA extensions;
CREATE EXTENSION pg_trgm SCHEMA extensions;

-- 2. Track extensions in version control
-- migrations/001_extensions.sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 3. Test extension compatibility
SELECT * FROM pg_available_extension_versions WHERE name = 'postgis';

-- 4. Monitor extension-specific stats
-- pg_stat_statements has its own views
-- PostGIS has geometry_columns, spatial_ref_sys

-- 5. Consider cloud compatibility
-- AWS RDS: Some extensions pre-installed, limited list
-- Azure: Similar restrictions
-- Self-hosted: Full flexibility
```

---

## 📝 Key Takeaways

1. **pg_stat_statements is essential** - Always install for production
2. **pg_trgm enables fuzzy search** - LIKE with wildcard performance
3. **PostGIS for geospatial** - Industry standard
4. **pg_cron for scheduling** - Database-level cron jobs
5. **Check cloud compatibility** - Not all extensions available

---

## ✅ Day 26 Checklist

- [ ] Enable pg_stat_statements
- [ ] Create trigram index for fuzzy search
- [ ] Practice PostGIS basics
- [ ] Schedule job with pg_cron
- [ ] Use pgcrypto for hashing
- [ ] Explore hstore and ltree
