# Day 22: JSONB & Document Storage

## 📚 Learning Objectives
- Master JSONB operators and functions
- Design hybrid relational/document schemas
- Index JSONB for performance
- Handle complex nested data

---

## 1. JSON vs JSONB

### Key Differences

| Feature | JSON | JSONB |
|---------|------|-------|
| Storage | Text (as-is) | Binary (parsed) |
| Write speed | Faster | Slower |
| Read speed | Slower | Faster |
| Duplicate keys | Preserved | Last value wins |
| Key ordering | Preserved | Not preserved |
| Indexing | Limited | Full GIN support |
| Functions | Limited | Full support |

```sql
-- Use JSONB for 99% of cases
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    metadata JSONB
);
```

---

## 2. JSONB Operators

### Extraction Operators

```sql
-- Sample data
INSERT INTO products (name, metadata) VALUES
('Laptop', '{
    "brand": "Dell",
    "specs": {
        "cpu": "i7",
        "ram": 16,
        "storage": {"type": "SSD", "size": 512}
    },
    "tags": ["electronics", "computers", "sale"],
    "price": 999.99
}');

-- -> returns JSON
SELECT metadata -> 'brand' FROM products;
-- Result: "Dell" (with quotes)

-- ->> returns text
SELECT metadata ->> 'brand' FROM products;
-- Result: Dell (no quotes)

-- Nested access
SELECT metadata -> 'specs' -> 'cpu' FROM products;
-- Result: "i7"

SELECT metadata #> '{specs,storage,type}' FROM products;
-- Result: "SSD"

-- Array element (0-indexed)
SELECT metadata -> 'tags' -> 0 FROM products;
-- Result: "electronics"

-- Last array element
SELECT metadata -> 'tags' -> -1 FROM products;
-- Result: "sale"
```

### Containment Operators

```sql
-- @> contains (right is subset of left)
SELECT * FROM products 
WHERE metadata @> '{"brand": "Dell"}';

-- <@ contained by (left is subset of right)
SELECT * FROM products 
WHERE '{"brand": "Dell"}'::jsonb <@ metadata;

-- ? key exists
SELECT * FROM products 
WHERE metadata ? 'brand';

-- ?| any of these keys exist
SELECT * FROM products 
WHERE metadata ?| array['brand', 'manufacturer'];

-- ?& all of these keys exist
SELECT * FROM products 
WHERE metadata ?& array['brand', 'specs'];
```

### Path Operators

```sql
-- @? path exists (returns boolean)
SELECT * FROM products 
WHERE metadata @? '$.specs.cpu';

-- @@ path match (JSON path predicate)
SELECT * FROM products 
WHERE metadata @@ '$.specs.ram > 8';

SELECT * FROM products 
WHERE metadata @@ '$.tags[*] == "sale"';
```

---

## 3. JSONB Functions

### Construction

```sql
-- Build JSON object
SELECT jsonb_build_object(
    'name', 'John',
    'age', 30,
    'active', true
);
-- Result: {"age": 30, "name": "John", "active": true}

-- Build JSON array
SELECT jsonb_build_array(1, 2, 'three', null);
-- Result: [1, 2, "three", null]

-- Aggregate to object
SELECT jsonb_object_agg(key, value)
FROM (VALUES ('a', 1), ('b', 2)) AS t(key, value);
-- Result: {"a": 1, "b": 2}

-- Aggregate to array
SELECT jsonb_agg(name) FROM products;
-- Result: ["Laptop", "Phone", ...]
```

### Manipulation

```sql
-- || concatenate/merge
SELECT '{"a": 1}'::jsonb || '{"b": 2}'::jsonb;
-- Result: {"a": 1, "b": 2}

-- - remove key
SELECT '{"a": 1, "b": 2}'::jsonb - 'a';
-- Result: {"b": 2}

-- - remove array element by index
SELECT '["a", "b", "c"]'::jsonb - 1;
-- Result: ["a", "c"]

-- #- remove by path
SELECT '{"a": {"b": 1}}'::jsonb #- '{a,b}';
-- Result: {"a": {}}

-- jsonb_set (update/insert at path)
SELECT jsonb_set(
    '{"a": {"b": 1}}'::jsonb,
    '{a,b}',
    '2'
);
-- Result: {"a": {"b": 2}}

-- Insert missing key
SELECT jsonb_set(
    '{"a": 1}'::jsonb,
    '{b}',
    '2',
    true  -- create_missing
);
-- Result: {"a": 1, "b": 2}

-- jsonb_insert (insert into array)
SELECT jsonb_insert(
    '["a", "c"]'::jsonb,
    '{1}',
    '"b"'
);
-- Result: ["a", "b", "c"]
```

### Inspection

```sql
-- typeof
SELECT jsonb_typeof('{"a": 1}'::jsonb);           -- object
SELECT jsonb_typeof('[1, 2]'::jsonb);             -- array
SELECT jsonb_typeof('"hello"'::jsonb);            -- string
SELECT jsonb_typeof('123'::jsonb);                -- number

-- array_length
SELECT jsonb_array_length('["a", "b", "c"]'::jsonb);
-- Result: 3

-- object keys
SELECT jsonb_object_keys('{"a": 1, "b": 2}'::jsonb);
-- Returns: a, b (as rows)

-- pretty print
SELECT jsonb_pretty('{"a":{"b":1}}'::jsonb);
```

### Expansion

```sql
-- Expand object to rows
SELECT * FROM jsonb_each('{"a": 1, "b": 2}'::jsonb);
-- key | value
-- a   | 1
-- b   | 2

SELECT * FROM jsonb_each_text('{"a": 1, "b": 2}'::jsonb);
-- key | value (as text)

-- Expand array to rows
SELECT * FROM jsonb_array_elements('[1, 2, 3]'::jsonb);
-- value
-- 1
-- 2
-- 3

SELECT * FROM jsonb_array_elements_text('["a", "b"]'::jsonb);

-- Convert to record
CREATE TYPE product_type AS (brand text, price numeric);

SELECT * FROM jsonb_populate_record(
    null::product_type,
    '{"brand": "Dell", "price": 999.99}'
);
-- brand | price
-- Dell  | 999.99
```

---

## 4. Indexing JSONB

### GIN Index (Default)

```sql
-- Index entire JSONB column
CREATE INDEX idx_products_metadata ON products USING GIN (metadata);

-- Supports:
-- @> containment
-- ? key existence
-- ?| any key exists
-- ?& all keys exist

-- Query using index
EXPLAIN SELECT * FROM products 
WHERE metadata @> '{"brand": "Dell"}';
-- Bitmap Index Scan on idx_products_metadata
```

### GIN with jsonb_path_ops

```sql
-- Smaller index, only @> supported
CREATE INDEX idx_products_metadata_path 
ON products USING GIN (metadata jsonb_path_ops);

-- Only for containment queries
SELECT * FROM products WHERE metadata @> '{"brand": "Dell"}';
```

### Expression Index (Specific Path)

```sql
-- Index specific key for equality
CREATE INDEX idx_products_brand 
ON products ((metadata ->> 'brand'));

-- Query uses btree index
SELECT * FROM products WHERE metadata ->> 'brand' = 'Dell';

-- Index for numeric comparisons
CREATE INDEX idx_products_price 
ON products (((metadata ->> 'price')::numeric));

SELECT * FROM products 
WHERE (metadata ->> 'price')::numeric < 500;
```

### Compare Index Strategies

```
Full GIN (jsonb_ops):
+ All operators supported
+ Flexible queries
- Larger index
- Slower updates

GIN (jsonb_path_ops):
+ Smaller (2-3x)
+ Faster updates
- Only @> supported

Expression index:
+ Fastest for specific key
+ Smallest
- Only that one path
```

---

## 5. Hybrid Schema Design

### When to Use JSONB

```sql
-- ✓ Good: Variable attributes
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,        -- Fixed, searchable
    sku VARCHAR(50) UNIQUE NOT NULL,   -- Fixed, unique
    attributes JSONB                    -- Variable by product type
);

-- ✓ Good: Event/audit logs
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    occurred_at TIMESTAMPTZ DEFAULT now(),
    payload JSONB
);

-- ✗ Bad: Core business data that needs constraints
-- Don't store user.email in JSONB if you need UNIQUE constraint
```

### Denormalization with JSONB

```sql
-- Embed related data
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    -- Snapshot of customer at order time
    customer_snapshot JSONB,
    items JSONB,  -- Array of order items
    status VARCHAR(20)
);

-- Query embedded array
SELECT 
    id,
    item->>'name' AS item_name,
    (item->>'quantity')::int AS qty,
    (item->>'price')::numeric AS price
FROM orders,
LATERAL jsonb_array_elements(items) AS item
WHERE id = 123;
```

---

## 6. Advanced Patterns

### Upsert with JSONB Merge

```sql
-- Atomic JSON update
UPDATE products
SET metadata = metadata || '{"on_sale": true}'
WHERE id = 1;

-- Deep merge (custom function)
CREATE OR REPLACE FUNCTION jsonb_merge_deep(a JSONB, b JSONB)
RETURNS JSONB AS $$
SELECT 
    COALESCE(a, '{}'::jsonb) || COALESCE(b, '{}'::jsonb)
    -- For true deep merge, use recursive function or extension
$$ LANGUAGE sql IMMUTABLE;
```

### Query Nested Arrays

```sql
-- Find products with specific tag
SELECT * FROM products
WHERE metadata -> 'tags' ? 'sale';

-- Find products where ANY tag matches pattern
SELECT * FROM products
WHERE EXISTS (
    SELECT 1 FROM jsonb_array_elements_text(metadata -> 'tags') AS tag
    WHERE tag LIKE '%computer%'
);

-- Aggregate nested array values
SELECT 
    id,
    jsonb_agg(DISTINCT tag) AS unique_tags
FROM products,
LATERAL jsonb_array_elements_text(metadata -> 'tags') AS tag
GROUP BY id;
```

### Generated Columns

```sql
-- Auto-extract JSONB values to columns
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    metadata JSONB,
    -- Generated columns from JSONB
    brand TEXT GENERATED ALWAYS AS (metadata ->> 'brand') STORED,
    price NUMERIC GENERATED ALWAYS AS 
        ((metadata ->> 'price')::numeric) STORED
);

-- Now you can index/query directly
CREATE INDEX idx_products_brand ON products (brand);
SELECT * FROM products WHERE brand = 'Dell';
```

---

## 7. Performance Tips

```sql
-- 1. Use containment for indexed lookups
-- Good (uses GIN index)
WHERE metadata @> '{"brand": "Dell"}'

-- Bad (no index, scans all rows)
WHERE metadata ->> 'brand' = 'Dell'

-- 2. Create expression indexes for specific paths
CREATE INDEX ON products ((metadata ->> 'brand'));
-- Now this is fast:
WHERE metadata ->> 'brand' = 'Dell'

-- 3. Avoid large JSONB updates
-- Bad: Full replace every time
UPDATE products SET metadata = '{"new": "big", "json": "object"}'

-- Good: Targeted update
UPDATE products SET metadata = metadata || '{"new_key": "value"}'

-- 4. Use TOAST wisely (auto for > 2KB)
-- Large JSONB compressed automatically
```

---

## 📝 Key Takeaways

1. **JSONB over JSON** - Binary format, indexable
2. **@> for indexed searches** - Containment uses GIN
3. **Expression indexes** - For specific path queries
4. **Hybrid schemas** - Fixed columns + JSONB flexibility
5. **Avoid full replaces** - Use || for updates

---

## ✅ Day 22 Checklist

- [ ] Practice JSONB operators (->>, @>)
- [ ] Create GIN index on JSONB column
- [ ] Create expression index for specific path
- [ ] Query nested arrays
- [ ] Design hybrid schema
- [ ] Use generated columns
