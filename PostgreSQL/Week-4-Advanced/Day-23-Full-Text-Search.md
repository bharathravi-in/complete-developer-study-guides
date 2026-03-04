# Day 23: Full-Text Search (FTS)

## 📚 Learning Objectives
- Understand FTS architecture
- Create and use tsvector/tsquery
- Configure text search dictionaries
- Optimize FTS performance

---

## 1. FTS Fundamentals

### Why Full-Text Search?

```sql
-- LIKE/ILIKE problems:
SELECT * FROM articles WHERE body LIKE '%database%';
-- ✗ No index usage (seq scan)
-- ✗ No relevance ranking
-- ✗ Case sensitive without ILIKE
-- ✗ No word stemming (search != searching)
-- ✗ No stop words handling

-- Full-Text Search benefits:
-- ✓ Index support (GIN/GiST)
-- ✓ Relevance ranking
-- ✓ Word stemming
-- ✓ Stop word removal
-- ✓ Language-aware
```

### Core Concepts

```
Document: "PostgreSQL is an advanced database system"
                        ↓
              Text Search Parser
                        ↓
Tokens: ["PostgreSQL", "is", "an", "advanced", "database", "system"]
                        ↓
              Text Search Dictionaries
                        ↓
Lexemes: ["postgresql", "advanc", "databas", "system"]
         (stop words "is", "an" removed, words stemmed)
                        ↓
              tsvector (searchable format)
'advanc':3 'databas':4 'postgresql':1 'system':5
```

---

## 2. tsvector and tsquery

### Creating tsvector

```sql
-- Basic conversion
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- Result: 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2

-- Note: "the" removed (stop word), "jumps" → "jump", "lazy" → "lazi"

-- Different language
SELECT to_tsvector('spanish', 'El perro corre rápidamente');

-- Simple configuration (no stemming)
SELECT to_tsvector('simple', 'PostgreSQL database');
-- Result: 'database':2 'postgresql':1
```

### Creating tsquery

```sql
-- Basic query
SELECT to_tsquery('english', 'database');
-- Result: 'databas' (stemmed)

-- Multiple terms (AND implicit)
SELECT to_tsquery('english', 'postgres & database');
-- Result: 'postgr' & 'databas'

-- OR operator
SELECT to_tsquery('english', 'postgres | mysql');

-- NOT operator
SELECT to_tsquery('english', 'database & !mysql');

-- Phrase query (adjacent terms)
SELECT to_tsquery('english', 'open <-> source');
-- "open source" as phrase

-- Proximity (within N words)
SELECT to_tsquery('english', 'database <2> performance');
-- "database" within 2 words of "performance"

-- Prefix matching
SELECT to_tsquery('english', 'post:*');
-- Matches postgres, postgresql, post, etc.
```

### Matching

```sql
-- @@ match operator
SELECT to_tsvector('english', 'PostgreSQL is a great database')
    @@ to_tsquery('english', 'database');
-- Result: true

SELECT to_tsvector('english', 'PostgreSQL is a great database')
    @@ to_tsquery('english', 'mysql');
-- Result: false

-- Practical query
SELECT title, body
FROM articles
WHERE to_tsvector('english', title || ' ' || body) 
    @@ to_tsquery('english', 'postgres & performance');
```

---

## 3. FTS on Tables

### Basic Setup

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    body TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Add tsvector column
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- Populate tsvector
UPDATE articles SET 
    search_vector = to_tsvector('english', 
        COALESCE(title, '') || ' ' || COALESCE(body, '')
    );

-- Create trigger to auto-update
CREATE OR REPLACE FUNCTION articles_search_trigger()
RETURNS trigger AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.body, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_articles_search
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION articles_search_trigger();
```

### Weighted Search

```sql
-- Weights: A > B > C > D (default is D)
-- Title more important than body

UPDATE articles SET search_vector = 
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(body, '')), 'B');

-- Query with ranking
SELECT 
    title,
    ts_rank(search_vector, query) AS rank
FROM articles,
    to_tsquery('english', 'database') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 10;

-- ts_rank considers weights automatically
```

---

## 4. Indexing FTS

### GIN Index (Recommended)

```sql
-- Create GIN index on tsvector column
CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);

-- Query uses index
EXPLAIN SELECT * FROM articles
WHERE search_vector @@ to_tsquery('english', 'database');
-- Bitmap Index Scan on idx_articles_search

-- Index on expression (if no stored tsvector)
CREATE INDEX idx_articles_fts ON articles 
USING GIN (to_tsvector('english', title || ' ' || body));
```

### GiST Index

```sql
-- GiST: Smaller, slower queries, faster updates
CREATE INDEX idx_articles_gist ON articles USING GiST (search_vector);

-- Use GiST when:
-- - Frequent updates
-- - Need KNN distance queries
-- - Combined with other GiST-able data
```

---

## 5. Text Search Configuration

### View Configurations

```sql
-- List available configurations
SELECT cfgname FROM pg_ts_config;
-- danish, dutch, english, finnish, french, german, hungarian, italian,
-- norwegian, portuguese, romanian, russian, simple, spanish, swedish, turkish

-- Set default
SET default_text_search_config = 'english';

-- View configuration details
\dF+ english
```

### Custom Dictionary

```sql
-- Create synonym dictionary
CREATE TEXT SEARCH DICTIONARY my_synonyms (
    TEMPLATE = synonym,
    SYNONYMS = my_synonyms  -- file: /share/tsearch_data/my_synonyms.syn
);

-- my_synonyms.syn content:
-- pg postgresql
-- db database
-- sql structured query language

-- Create custom configuration
CREATE TEXT SEARCH CONFIGURATION my_config (COPY = english);

-- Add synonym dictionary
ALTER TEXT SEARCH CONFIGURATION my_config
    ALTER MAPPING FOR asciiword
    WITH my_synonyms, english_stem;

-- Use custom config
SELECT to_tsvector('my_config', 'pg is a great db');
-- 'databas':5 'great':4 'postgresql':1
```

### Stop Words

```sql
-- View stop words
SELECT * FROM ts_debug('english', 'The quick brown fox');
-- "the" marked as stop word

-- Create configuration without stop words
CREATE TEXT SEARCH CONFIGURATION no_stop (COPY = simple);
-- simple config has no stop words or stemming
```

---

## 6. Advanced FTS Features

### Highlighting Results

```sql
-- ts_headline highlights matching terms
SELECT 
    ts_headline('english', body, to_tsquery('english', 'database'),
        'StartSel=<b>, StopSel=</b>, MaxWords=35, MinWords=15'
    ) AS highlighted
FROM articles
WHERE search_vector @@ to_tsquery('english', 'database');

-- Result: ...PostgreSQL is a powerful <b>database</b> system that...
```

### Plain Text Query

```sql
-- User-friendly query parsing
SELECT plainto_tsquery('english', 'open source database');
-- Result: 'open' & 'sourc' & 'databas'

SELECT phraseto_tsquery('english', 'open source');
-- Result: 'open' <-> 'sourc'

SELECT websearch_to_tsquery('english', '"open source" database -mysql');
-- Result: 'open' <-> 'sourc' & 'databas' & !'mysql'
-- Supports: quotes for phrases, - for exclusion, OR
```

### Ranking Functions

```sql
-- ts_rank: Frequency-based
SELECT ts_rank(search_vector, query) FROM ...

-- ts_rank_cd: Cover density (proximity matters more)
SELECT ts_rank_cd(search_vector, query) FROM ...

-- Normalize by document length
SELECT ts_rank(search_vector, query, 32) FROM ...
-- 32 = normalize by document length

-- Boost recent articles
SELECT 
    ts_rank(search_vector, query) * 
    (1.0 / (EXTRACT(EPOCH FROM now() - created_at) / 86400 + 1)) AS score
FROM articles
ORDER BY score DESC;
```

---

## 7. FTS with JSONB

```sql
-- Search within JSONB field
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    data JSONB,
    search_vector tsvector
);

-- Extract text from JSONB for FTS
CREATE OR REPLACE FUNCTION jsonb_to_tsvector_text(doc JSONB)
RETURNS TEXT AS $$
    SELECT string_agg(value, ' ')
    FROM jsonb_each_text(doc)
    WHERE key IN ('title', 'description', 'content')
$$ LANGUAGE sql IMMUTABLE;

-- Trigger for JSONB documents
CREATE OR REPLACE FUNCTION update_doc_search()
RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', 
        jsonb_to_tsvector_text(NEW.data)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 8. Performance Tips

```sql
-- 1. Store tsvector column (vs computing on-the-fly)
-- Good: Pre-computed
WHERE search_vector @@ query

-- Bad: Computed per row (no index)
WHERE to_tsvector('english', title || ' ' || body) @@ query

-- 2. Use GIN for read-heavy workloads
CREATE INDEX idx_fts USING GIN (search_vector);

-- 3. Limit result set before ranking
WITH matches AS (
    SELECT id, search_vector
    FROM articles
    WHERE search_vector @@ query
    LIMIT 1000  -- Cap matches
)
SELECT id, ts_rank(search_vector, query) AS rank
FROM matches
ORDER BY rank DESC
LIMIT 20;

-- 4. Use websearch_to_tsquery for user input
-- Handles malformed queries gracefully
```

---

## 📝 Key Takeaways

1. **tsvector for documents** - Normalized, indexed format
2. **tsquery for searches** - Boolean and phrase queries
3. **GIN index for FTS** - Fast lookups
4. **Store tsvector column** - Avoid recomputation
5. **Weights for ranking** - Title > Body

---

## ✅ Day 23 Checklist

- [ ] Create tsvector column
- [ ] Build FTS trigger
- [ ] Create GIN index
- [ ] Practice tsquery operators
- [ ] Implement search with ranking
- [ ] Add highlight functionality
