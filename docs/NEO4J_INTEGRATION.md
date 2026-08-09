# Neo4j Integration in MarketSensing

## Purpose

Neo4j is used as a **knowledge graph** to track:
1. **Data lineage** — which data source feeds into which features
2. **Feature dependencies** — which features depend on which data sources
3. **Model dependencies** — which features are used by which ML models
4. **Impact analysis** — if a data source breaks, which signals are affected?
5. **Audit trail** — trace any signal back to its source data and calculation

**PostgreSQL** stores the operational data (prices, spreads, signals).  
**Neo4j** stores the *relationships* (data → features → models → signals).

---

## Graph Schema

### Nodes

#### DataSource
```cypher
:DataSource {
  name: "NYMEX",
  category: "Market Data",
  description: "NYMEX futures (WTI, RBOB, ULSD)",
  created_at: timestamp
}
```

#### Feature
```cypher
:Feature {
  name: "spread_z_score_60d",
  type: "spread_statistic",
  lookback_days: 60,
  created_at: timestamp
}
```

#### Model
```cypher
:Model {
  model_id: "wti_midland_cushing_v1",
  commodity: "WTI",
  leap_duration: 3,  # days
  created_at: timestamp
}
```

#### Signal
```cypher
:Signal {
  signal_id: "uuid",
  strategy: "spread_midland_cushing",
  timestamp: "2026-08-09T...",
  action: "BUY"
}
```

### Relationships

```
DataSource --[PROVIDES_DATA_FOR]--> Feature
Feature --[USES]--> Model
Model --[GENERATES]--> Signal
```

**Reverse queries**: "If NYMEX goes down, which signals will be affected?"

---

## Use Cases

### 1. **Data Lineage Tracking**
When someone asks: "Where does this signal come from?", trace back:

```cypher
MATCH (s:Signal {signal_id: "uuid"})-[r1:GENERATED_BY]->(m:Model)
       -[r2:USES]->(f:Feature)-[r3:DEPENDS_ON]->(ds:DataSource)
RETURN ds.name, f.name, m.model_id, s.action
```

**Result**: "Signal BUY came from NYMEX (futures) → spread_z_score_60d (feature) → wti_model_v1"

---

### 2. **Impact Analysis**
When a data source is down, find affected signals:

```cypher
MATCH (ds:DataSource {name: "NYMEX"})<-[r1:DEPENDS_ON]-(f:Feature)
       <-[r2:USES]-(m:Model)<-[r3:GENERATED_BY]-(s:Signal)
WHERE s.timestamp > datetime.now() - duration("P1D")  # Last 24h signals
RETURN COUNT(DISTINCT s) as affected_signals
```

**Result**: "NYMEX outage affects 47 signals generated in last 24h"

---

### 3. **Feature Importance (Via Graph)**
Which data sources are most critical?

```cypher
MATCH (ds:DataSource)<-[r:DEPENDS_ON]-(f:Feature)
       <-[r2:USES]-(m:Model)
RETURN ds.name, COUNT(DISTINCT f) as feature_count, COUNT(DISTINCT m) as model_count
ORDER BY model_count DESC
```

**Result**: 
| Data Source | Features | Models |
|---|---|---|
| NYMEX | 15 | 23 |
| EIA | 8 | 12 |
| Kpler | 5 | 7 |

---

### 4. **Audit Trail**
For compliance/risk: prove where every signal comes from.

```cypher
MATCH (s:Signal {signal_id: $signal_id})-[r:GENERATED_BY]->(m:Model)
RETURN s, m, r
```

---

## Implementation Status

### Current (MVP Phase)
- Neo4j server running locally (community edition)
- Basic graph schema defined
- No data populating the graph yet

### Phase 1 (After Core Signal Works)
- Populate graph as signals are generated:
  ```python
  # After generating a signal
  signal = await use_case.execute(request)
  await neo4j_db.add_signal_lineage(
      signal_id=signal.signal_id,
      model_id="wti_model_v1",
      strategy_id=signal.strategy_id,
      timestamp=signal.timestamp.isoformat()
  )
  ```

### Phase 2 (Production)
- Real-time impact analysis when data sources change
- Dashboard query: "Which commodities are affected if NYMEX is down?"
- Automated alerts: "Last 3 EIA features are stale (>24h old)"

---

## Cypher Queries (Ready to Use)

### Setup (Run Once)
```cypher
CREATE INDEX data_sources_name IF NOT EXISTS FOR (n:DataSource) ON (n.name);
CREATE INDEX features_name IF NOT EXISTS FOR (n:Feature) ON (n.name);
CREATE INDEX models_id IF NOT EXISTS FOR (n:Model) ON (n.model_id);
CREATE INDEX signals_id IF NOT EXISTS FOR (n:Signal) ON (n.signal_id);
```

### Add Data Source
```cypher
MERGE (ds:DataSource {name: "NYMEX"})
SET ds.category = "Market Data", 
    ds.description = "NYMEX futures (WTI, RBOB, ULSD)",
    ds.created_at = datetime()
RETURN ds;
```

### Add Feature
```cypher
MERGE (f:Feature {name: "spread_z_score_60d"})
SET f.type = "spread_statistic",
    f.lookback_days = 60,
    f.created_at = datetime()
RETURN f;
```

### Link Feature to Data Source
```cypher
MATCH (f:Feature {name: "spread_z_score_60d"})
MATCH (ds:DataSource {name: "NYMEX"})
MERGE (f)-[r:DEPENDS_ON]->(ds)
SET r.created_at = datetime()
RETURN f, ds;
```

### Get Impact Chain
```cypher
MATCH (ds:DataSource {name: "NYMEX"})<-[r1:DEPENDS_ON]-(f:Feature)
       <-[r2:USES]-(m:Model)<-[r3:GENERATED_BY]-(s:Signal)
RETURN 
  ds.name as data_source,
  COLLECT(DISTINCT f.name) as affected_features,
  COLLECT(DISTINCT m.model_id) as affected_models,
  COLLECT(DISTINCT s.signal_id) as affected_signals;
```

---

## Why Not Use PostgreSQL for This?

**Neo4j is better for relationships** because:
- Recursive queries (lineage) are 1000x faster in Neo4j
- No need for SQL JOINs on N levels deep (data → 5 features → 10 models → 100 signals)
- Graph visualizations (Bloom, GraphXR) make impact analysis obvious
- Pattern matching is intuitive (`MATCH (...)-[...]->(...) WHERE ...`)

**PostgreSQL would need**: Recursive CTEs, multiple JOINs, complex indexes, and would be slow.

---

## Production Deployment

### Docker Compose Entry (for later)
```yaml
neo4j:
  image: neo4j:latest
  environment:
    NEO4J_AUTH: neo4j/marketsensing-password
    NEO4J_PLUGINS: "[\"apoc\"]"
  ports:
    - "7687:7687"  # Bolt (driver)
    - "7474:7474"  # Browser UI
  volumes:
    - neo4j_data:/data
```

### Environment Variables
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=marketsensing-password
```

---

## Access

### Browser UI
Navigate to: **http://localhost:7474**  
Username: `neo4j`  
Password: Your configured password

### CLI (cypher-shell)
```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p <password>
```

### Python Driver (in code)
```python
from src.infrastructure.neo4j import Neo4jDatabase

neo4j = Neo4jDatabase(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="marketsensing-password"
)
await neo4j.connect()
impact = await neo4j.get_impact_chain("NYMEX")
print(f"NYMEX outage affects {len(impact['signals'])} signals")
```

---

## Summary

| Aspect | Neo4j | PostgreSQL |
|---|---|---|
| **What** | Knowledge graph of dependencies | Operational trading data |
| **Use** | Impact analysis, lineage | Prices, spreads, signals |
| **Query Style** | Graph patterns | SQL, JOINs |
| **Strength** | Relationship queries | Time-series, ACID |

**Both are needed**: PostgreSQL for transactions, Neo4j for insight.
