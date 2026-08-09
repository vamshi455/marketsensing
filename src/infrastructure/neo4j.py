"""Neo4j database for knowledge graph and lineage tracking."""
from neo4j import AsyncDriver, AsyncSession, graphene, Config


class Neo4jDatabase:
    """Neo4j connection and operations."""

    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j driver."""
        self.uri = uri
        self.driver: AsyncDriver = None
        self.config = Config(encrypted=False)
        self._user = user
        self._password = password

    async def connect(self):
        """Create connection."""
        from neo4j import AsyncGraphDatabase

        self.driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self._user, self._password),
            config=self.config,
        )

    async def disconnect(self):
        """Close connection."""
        if self.driver:
            await self.driver.close()

    async def create_schema(self):
        """Create knowledge graph schema (indices)."""
        async with self.driver.session() as session:
            queries = [
                "CREATE INDEX data_sources_name IF NOT EXISTS FOR (n:DataSource) ON (n.name)",
                "CREATE INDEX features_name IF NOT EXISTS FOR (n:Feature) ON (n.name)",
                "CREATE INDEX models_id IF NOT EXISTS FOR (n:Model) ON (n.model_id)",
                "CREATE INDEX signals_id IF NOT EXISTS FOR (n:Signal) ON (n.signal_id)",
            ]
            for query in queries:
                await session.run(query)

    async def add_data_source(self, name: str, category: str, description: str):
        """Add a data source node."""
        query = """
        MERGE (ds:DataSource {name: $name})
        SET ds.category = $category, ds.description = $description, ds.created_at = datetime()
        RETURN ds
        """
        async with self.driver.session() as session:
            await session.run(query, name=name, category=category, description=description)

    async def add_feature(self, name: str, feature_type: str, lookback_days: int):
        """Add a feature node."""
        query = """
        MERGE (f:Feature {name: $name})
        SET f.type = $type, f.lookback_days = $lookback_days, f.created_at = datetime()
        RETURN f
        """
        async with self.driver.session() as session:
            await session.run(
                query, name=name, type=feature_type, lookback_days=lookback_days
            )

    async def add_model(self, model_id: str, commodity: str, leap_duration: int):
        """Add a model node."""
        query = """
        MERGE (m:Model {model_id: $model_id})
        SET m.commodity = $commodity, m.leap_duration = $leap_duration, m.created_at = datetime()
        RETURN m
        """
        async with self.driver.session() as session:
            await session.run(
                query,
                model_id=model_id,
                commodity=commodity,
                leap_duration=leap_duration,
            )

    async def link_feature_to_data_source(self, feature_name: str, data_source_name: str):
        """Create DEPENDS_ON relationship from feature to data source."""
        query = """
        MATCH (f:Feature {name: $feature_name})
        MATCH (ds:DataSource {name: $data_source_name})
        MERGE (f)-[r:DEPENDS_ON]->(ds)
        SET r.created_at = datetime()
        RETURN f, ds
        """
        async with self.driver.session() as session:
            await session.run(query, feature_name=feature_name, data_source_name=data_source_name)

    async def link_model_to_features(self, model_id: str, feature_names: list[str]):
        """Create USES relationship from model to features."""
        query = """
        MATCH (m:Model {model_id: $model_id})
        UNWIND $feature_names AS fname
        MATCH (f:Feature {name: fname})
        MERGE (m)-[r:USES]->(f)
        SET r.created_at = datetime()
        RETURN m, f
        """
        async with self.driver.session() as session:
            await session.run(query, model_id=model_id, feature_names=feature_names)

    async def add_signal_lineage(
        self,
        signal_id: str,
        model_id: str,
        strategy_id: str,
        timestamp: str,
    ):
        """Create signal node and link to model."""
        query = """
        CREATE (s:Signal {signal_id: $signal_id, strategy: $strategy_id, timestamp: $timestamp})
        WITH s
        MATCH (m:Model {model_id: $model_id})
        MERGE (s)-[r:GENERATED_BY]->(m)
        SET r.created_at = datetime()
        RETURN s, m
        """
        async with self.driver.session() as session:
            await session.run(
                query,
                signal_id=signal_id,
                model_id=model_id,
                strategy_id=strategy_id,
                timestamp=timestamp,
            )

    async def get_impact_chain(self, data_source_name: str) -> dict:
        """Get full impact chain: data source → features → models → signals."""
        query = """
        MATCH (ds:DataSource {name: $data_source_name})<-[r1:DEPENDS_ON]-(f:Feature)
        OPTIONAL MATCH (f)<-[r2:USES]-(m:Model)
        OPTIONAL MATCH (s:Signal)-[r3:GENERATED_BY]->(m)
        RETURN
            ds.name as data_source,
            COLLECT(DISTINCT f.name) as features,
            COLLECT(DISTINCT m.model_id) as models,
            COLLECT(DISTINCT s.signal_id) as signals
        """
        async with self.driver.session() as session:
            result = await session.run(query, data_source_name=data_source_name)
            record = await result.single()
            if record:
                return dict(record)
            return {}

    async def get_lineage_for_signal(self, signal_id: str) -> dict:
        """Get full lineage for a signal: what data/features/models produced it."""
        query = """
        MATCH (s:Signal {signal_id: $signal_id})-[r1:GENERATED_BY]->(m:Model)
        OPTIONAL MATCH (m)-[r2:USES]->(f:Feature)
        OPTIONAL MATCH (f)-[r3:DEPENDS_ON]->(ds:DataSource)
        RETURN
            s.signal_id as signal_id,
            s.timestamp as timestamp,
            m.model_id as model_id,
            COLLECT(DISTINCT {feature: f.name, source: ds.name}) as lineage
        """
        async with self.driver.session() as session:
            result = await session.run(query, signal_id=signal_id)
            record = await result.single()
            if record:
                return dict(record)
            return {}
