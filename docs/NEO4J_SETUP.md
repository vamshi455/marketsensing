# Neo4j Setup & Cypher Query Guide

## Installation Status ✅

**Version**: 2026.07.1 (Community Edition)  
**Status**: Running  
**Installation Method**: Homebrew

---

## Access Neo4j

### 1. Neo4j Browser (Web UI)
Open your browser and navigate to:
```
http://localhost:7474/browser
```

**Default Credentials:**
- Username: `neo4j`
- Password: `neo4j` (you'll be prompted to change on first login)

### 2. Cypher Shell (CLI)
Run queries directly from terminal:
```bash
cypher-shell
```

Then enter credentials and start typing Cypher queries.

### 3. REST API
```bash
curl -u neo4j:neo4j http://localhost:7474/db/neo4j/query/v2
```

---

## Manage Neo4j Service

### Start Neo4j
```bash
brew services start neo4j
```

### Stop Neo4j
```bash
brew services stop neo4j
```

### Restart Neo4j
```bash
brew services restart neo4j
```

### Check Status
```bash
brew services info neo4j
```

### Run in Foreground (for debugging)
```bash
/opt/homebrew/opt/neo4j/bin/neo4j console
```

---

## Cypher Query Language Basics

Cypher is Neo4j's query language. It uses ASCII-art syntax to represent graphs.

### 1. Create Nodes

```cypher
// Create a single node
CREATE (n:Person {name: "Alice", age: 30})

// Create multiple nodes
CREATE 
  (alice:Person {name: "Alice", age: 30}),
  (bob:Person {name: "Bob", age: 28}),
  (charlie:Person {name: "Charlie", age: 35})

// Return the created node
RETURN alice
```

### 2. Create Relationships

```cypher
// Create nodes and relationships
CREATE 
  (alice:Person {name: "Alice"})-[:KNOWS]->(bob:Person {name: "Bob"}),
  (bob)-[:KNOWS]->(charlie:Person {name: "Charlie"}),
  (alice)-[:MANAGES]->(bob)

RETURN alice, bob, charlie
```

### 3. Query Nodes

```cypher
// Find all people
MATCH (n:Person) RETURN n

// Find specific person
MATCH (n:Person {name: "Alice"}) RETURN n

// Find with conditions
MATCH (n:Person) WHERE n.age > 25 RETURN n.name, n.age

// Find by property
MATCH (n:Person) WHERE n.name STARTS WITH "A" RETURN n
```

### 4. Query Relationships

```cypher
// Find all relationships
MATCH (a:Person)-[r:KNOWS]->(b:Person) RETURN a, r, b

// Find specific relationships
MATCH (a:Person)-[:MANAGES]->(b:Person) RETURN a.name AS manager, b.name AS subordinate

// Multi-hop traversal
MATCH (a:Person)-[:KNOWS]->(b:Person)-[:KNOWS]->(c:Person) 
WHERE a.name = "Alice"
RETURN a.name, b.name, c.name
```

### 5. Update Data

```cypher
// Update a property
MATCH (n:Person {name: "Alice"})
SET n.age = 31
RETURN n

// Add a new property
MATCH (n:Person {name: "Alice"})
SET n.email = "alice@example.com"
RETURN n

// Add a label
MATCH (n:Person {name: "Alice"})
SET n:Manager
RETURN n
```

### 6. Delete Data

```cypher
// Delete nodes (must delete relationships first)
MATCH (n:Person {name: "Alice"})
DELETE n

// Delete relationships
MATCH (a:Person)-[r:KNOWS]->(b:Person)
DELETE r

// Delete everything
MATCH (n)
DETACH DELETE n
```

### 7. Aggregation

```cypher
// Count nodes
MATCH (n:Person) RETURN COUNT(n) AS total_people

// Count relationships
MATCH ()-[r:KNOWS]->() RETURN COUNT(r) AS total_knows_relations

// Group by
MATCH (n:Person) RETURN n.age, COUNT(n) AS count GROUP BY n.age

// Statistics
MATCH (n:Person) RETURN 
  MIN(n.age) AS min_age, 
  MAX(n.age) AS max_age, 
  AVG(n.age) AS avg_age
```

### 8. Sorting & Limiting

```cypher
// Sort ascending
MATCH (n:Person) RETURN n ORDER BY n.age

// Sort descending
MATCH (n:Person) RETURN n ORDER BY n.age DESC

// Limit results
MATCH (n:Person) RETURN n LIMIT 5

// Skip and limit (pagination)
MATCH (n:Person) RETURN n SKIP 5 LIMIT 10
```

### 9. Paths & Shortest Path

```cypher
// Find any path between two nodes
MATCH p = (a:Person {name: "Alice"})-[*]-(b:Person {name: "Charlie"})
RETURN p

// Shortest path
MATCH p = shortestPath((a:Person {name: "Alice"})-[*]-(b:Person {name: "Charlie"}))
RETURN p

// Path with constraints
MATCH p = (a:Person)-[:KNOWS*1..3]-(b:Person)
WHERE a.name = "Alice" AND b.name = "Charlie"
RETURN p
```

### 10. Create Indexes

```cypher
// Create index for faster queries
CREATE INDEX ON :Person(name)

// Create unique constraint
CREATE CONSTRAINT ON (p:Person) ASSERT p.email IS UNIQUE
```

---

## Example: MarketSensing Graph Model

Here's how you could model the MarketSensing system in Neo4j:

### Create Data Sources
```cypher
CREATE
  (nymex:DataSource {name: "NYMEX", frequency: "every second", type: "Trading Data"}),
  (kpler:DataSource {name: "Kpler", frequency: "daily", type: "Physical Flows"}),
  (eia:DataSource {name: "EIA", frequency: "weekly", type: "Inventory"}),
  (mpr:DataSource {name: "MPR/MIPS", frequency: "daily", type: "Internal Operations"})
RETURN nymex, kpler, eia, mpr
```

### Create Models
```cypher
CREATE
  (time_model:Model {name: "Time Spread Model", precision: 0.63}),
  (geo_model:Model {name: "Geographic Arbitrage", precision: 0.58}),
  (supply_model:Model {name: "Supply Shock Model", precision: 0.71})
RETURN time_model, geo_model, supply_model
```

### Create Relationships (Data Source → Model)
```cypher
MATCH (nymex:DataSource {name: "NYMEX"}), (time_model:Model {name: "Time Spread Model"})
CREATE (nymex)-[:FEEDS_INTO]->(time_model)

MATCH (kpler:DataSource {name: "Kpler"}), (geo_model:Model {name: "Geographic Arbitrage"})
CREATE (kpler)-[:FEEDS_INTO]->(geo_model)

MATCH (eia:DataSource {name: "EIA"}), (supply_model:Model {name: "Supply Shock Model"})
CREATE (eia)-[:FEEDS_INTO]->(supply_model)

MATCH (mpr:DataSource {name: "MPR/MIPS"}), (supply_model:Model {name: "Supply Shock Model"})
CREATE (mpr)-[:FEEDS_INTO]->(supply_model)
```

### Query the Graph
```cypher
// What data sources feed into the Time Spread Model?
MATCH (source:DataSource)-[:FEEDS_INTO]->(model:Model {name: "Time Spread Model"})
RETURN source.name, source.frequency

// What models use Kpler data?
MATCH (source:DataSource {name: "Kpler"})-[:FEEDS_INTO]->(model:Model)
RETURN model.name, model.precision

// Full data lineage
MATCH (source:DataSource)-[:FEEDS_INTO]->(model:Model)
RETURN source.name, model.name, source.frequency
```

---

## Useful Cypher Functions

```cypher
-- String Functions
MATCH (n:Person) RETURN 
  UPPER(n.name),           -- "ALICE"
  LOWER(n.name),           -- "alice"
  SIZE(n.name),            -- 5
  SUBSTRING(n.name, 0, 2)  -- "Al"

-- Numeric Functions
RETURN ABS(-5), CEIL(3.2), FLOOR(3.8), ROUND(3.5)
-- 5, 4, 3, 4

-- Date Functions
RETURN date(), datetime(), timestamp()

-- Collection Functions
MATCH (n:Person) RETURN COLLECT(n.name) AS names
MATCH (n:Person) RETURN [n.name | n.name STARTS WITH "A"] AS names_starting_with_a
```

---

## Performance Tips

1. **Always use indexes** on frequently searched properties
   ```cypher
   CREATE INDEX ON :Person(name)
   ```

2. **Use EXPLAIN** to see query execution plan
   ```cypher
   EXPLAIN MATCH (n:Person) RETURN n
   ```

3. **Use PROFILE** to see actual execution stats
   ```cypher
   PROFILE MATCH (n:Person) RETURN n
   ```

4. **Limit results** when dealing with large datasets
   ```cypher
   MATCH (n:Person) RETURN n LIMIT 1000
   ```

5. **Use query parameters** to prevent injection
   ```cypher
   MATCH (n:Person {name: $name}) RETURN n
   // Run with: {name: "Alice"}
   ```

---

## Resources

- **Neo4j Browser**: http://localhost:7474/browser
- **Neo4j Documentation**: https://neo4j.com/docs/
- **Cypher Cheat Sheet**: https://neo4j.com/docs/cypher-manual/current/
- **Neo4j Community**: https://community.neo4j.com/

---

## Quick Troubleshooting

### Neo4j not starting?
```bash
# Check if port 7474 is in use
lsof -i :7474

# Force stop any lingering processes
killall neo4j java

# Start fresh
brew services stop neo4j
brew services start neo4j
```

### Forgot password?
1. Stop Neo4j
2. Delete the auth file:
   ```bash
   rm /opt/homebrew/var/neo4j/data/dbms/auth
   ```
3. Start Neo4j (will reset to default `neo4j:neo4j`)

### Check logs
```bash
tail -f /opt/homebrew/var/neo4j/logs/neo4j.log
```

---

**Edition**: Community (free, all essential features)  
**Bolt Port**: 7687  
**HTTP Port**: 7474 (Browser)  
**Browser URL**: http://localhost:7474/browser
