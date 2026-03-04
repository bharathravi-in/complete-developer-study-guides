# Day 10: Sharding Strategies

## What Is Sharding?

Sharding = **horizontal partitioning** across multiple database instances. Each shard holds a subset of the data with the same schema.

```
┌──────────────────────────────────────────┐
│              Application Layer            │
├──────────┬──────────┬──────────┬─────────┤
│ Shard 0  │ Shard 1  │ Shard 2  │ Shard 3│
│Users A-F │Users G-L │Users M-R │Users S-Z│
│ Server 1 │ Server 2 │ Server 3 │Server 4 │
└──────────┘──────────┘──────────┘─────────┘
```

## When to Shard

```
DON'T shard unless:
✅ Single server can't handle write volume
✅ Data doesn't fit on one machine (> 1-5 TB)
✅ Read replicas can't handle read volume
✅ You've exhausted: indexing, caching, read replicas, vertical scaling

Shard when:
✅ Need > 10K write TPS sustained
✅ Need horizontal write scalability
✅ Need data locality (geo-sharding)
```

## Sharding Strategies

### 1. Range-Based Sharding

```
Shard by ranges of the shard key:
Shard 0: user_id 1 - 1,000,000
Shard 1: user_id 1,000,001 - 2,000,000
Shard 2: user_id 2,000,001 - 3,000,000
```

**Pros**: Range queries efficient, easy to understand
**Cons**: Hot spots (new users all go to latest shard), uneven distribution

```python
def get_shard(user_id: int, shard_ranges: list) -> int:
    for i, (start, end) in enumerate(shard_ranges):
        if start <= user_id <= end:
            return i
    raise ValueError(f"No shard for user_id {user_id}")
```

### 2. Hash-Based Sharding

```
shard_id = hash(shard_key) % num_shards

hash("user_123") % 4 = 2 → Shard 2
hash("user_456") % 4 = 0 → Shard 0
hash("user_789") % 4 = 3 → Shard 3
```

**Pros**: Even distribution, no hot spots
**Cons**: Range queries require scatter-gather, adding shards requires rehashing

```python
import hashlib

def get_shard(key: str, num_shards: int) -> int:
    hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return hash_val % num_shards
```

### 3. Consistent Hashing

Solves the rehashing problem when adding/removing shards.

```
        Hash Ring (0 — 2^32)
           ┌───────┐
      S0──>│       │<──S1
           │  Ring │
      S3──>│       │<──S2
           └───────┘

Key → hash → walk clockwise → first server = shard

Adding S4: Only keys between S3 and S4 need to move
Removing S1: Only S1's keys move to S2
```

```python
import hashlib
from bisect import bisect_right

class ConsistentHash:
    def __init__(self, nodes: list[str], virtual_nodes: int = 150):
        self.ring: dict[int, str] = {}
        self.sorted_keys: list[int] = []
        
        for node in nodes:
            for i in range(virtual_nodes):
                key = self._hash(f"{node}:{i}")
                self.ring[key] = node
                self.sorted_keys.append(key)
        
        self.sorted_keys.sort()
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def get_node(self, key: str) -> str:
        if not self.ring:
            raise ValueError("Empty ring")
        h = self._hash(key)
        idx = bisect_right(self.sorted_keys, h) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]

# Usage
ch = ConsistentHash(["shard-0", "shard-1", "shard-2", "shard-3"])
shard = ch.get_node("user_123")  # → "shard-2"
```

### 4. Directory-Based Sharding

Lookup service maps keys to shards:

```
┌─────────────────────────┐
│   Shard Directory (DB)  │
│  key_range  │  shard_id │
│  user_1-1M  │  shard_0  │
│  user_1M-2M │  shard_1  │
└─────────────────────────┘

App → Directory lookup → Route to shard
```

**Pros**: Maximum flexibility, easy resharding
**Cons**: Directory is SPOF, adds latency

### 5. Geo-Based Sharding

```
Shard by geographic region:
US-East:  user.region = 'us-east'  → us-east-db.example.com 
EU-West:  user.region = 'eu-west'  → eu-west-db.example.com
AP-South: user.region = 'ap-south' → ap-south-db.example.com
```

**Use case**: Data sovereignty (GDPR), latency reduction

## Shard Key Selection — The Most Critical Decision

### Good Shard Keys
```
✅ High cardinality (many unique values)
✅ Even distribution across shards
✅ Queries naturally include the shard key
✅ Doesn't change over time (immutable)
✅ Low cross-shard query need
```

### Shard Key Examples

| System | Good Key | Why |
|--------|----------|-----|
| E-commerce | `customer_id` | Most queries are per-customer |
| Social media | `user_id` | Feed/profile queries are per-user |
| Multi-tenant SaaS | `tenant_id` | Data isolation per tenant |
| Time-series | `timestamp` range | Queries are time-bounded |
| Chat app | `conversation_id` | Messages group by conversation |

### Bad Shard Keys
```
❌ Low cardinality: country (only ~200 values → uneven distribution)
❌ Monotonically increasing: auto-increment ID with range sharding → hot shard
❌ Frequently updated: email (changes shard location)
❌ Rarely in queries: created_date for user lookups
```

### Compound Shard Keys
```
shard_key = (tenant_id, user_id)

Benefits:
- tenant_id ensures tenant isolation per shard
- user_id provides distribution within a tenant
- Queries on both fields route to single shard
```

## Cross-Shard Query Patterns

### Scatter-Gather
```
Query: SELECT * FROM users WHERE age > 25

App → Send query to ALL shards
   ← Collect results from each shard
   → Merge and return
```
Expensive — avoid in hot paths.

### Global Tables
```
Small, rarely-changing tables replicated to ALL shards:
- Countries, currencies, configuration
- Read locally, update via broadcast
```

### Shard-Aware Application Layer
```python
class ShardRouter:
    def route_query(self, query, params):
        if 'user_id' in params:
            # Single-shard query
            shard = self.get_shard(params['user_id'])
            return shard.execute(query, params)
        else:
            # Cross-shard scatter-gather
            results = []
            for shard in self.all_shards:
                results.extend(shard.execute(query, params))
            return self.merge_results(results)
```

## Resharding — Adding More Shards

### The Problem
```
hash(key) % 4 = shard_2
hash(key) % 5 = shard_3  ← Different shard after adding one!
```

### Solutions
1. **Consistent hashing**: Only ~1/N keys move when adding N-th node
2. **Virtual shards**: Pre-create more shards than physical nodes, reassign as needed
3. **Double-write migration**: Write to old + new, backfill, switch reads, stop old writes

## Key Takeaways

1. **Don't shard unless necessary** — it adds enormous complexity
2. **Shard key selection is irreversible** — get it right the first time
3. **Consistent hashing** solves the rehashing problem
4. **Cross-shard queries are expensive** — design schema to minimize them
5. **Pre-shard with virtual shards** to avoid painful resharding later
