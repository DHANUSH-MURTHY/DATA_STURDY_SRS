"""
Neo4j client — singleton driver with demo-mode fallback.
"""
import logging
from neo4j import GraphDatabase
from config import settings

logger = logging.getLogger(__name__)


class Neo4jClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._driver = None
        return cls._instance

    # ------------------------------------------------------------------ #
    def connect(self):
        if settings.DEMO_MODE:
            logger.info("DEMO_MODE active — Neo4j connection skipped.")
            return
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            )
            self._driver.verify_connectivity()
            logger.info("Connected to Neo4j at %s", settings.NEO4J_URI)
        except Exception as exc:
            logger.warning("Neo4j unavailable (%s) — falling back to demo mode.", exc)
            self._driver = None

    def close(self):
        if self._driver:
            self._driver.close()

    @property
    def is_connected(self) -> bool:
        return self._driver is not None

    # ------------------------------------------------------------------ #
    def run_query(self, cypher: str, params: dict | None = None) -> list[dict]:
        if not self.is_connected:
            return []
        with self._driver.session() as session:
            result = session.run(cypher, params or {})
            return [record.data() for record in result]

    def run_write(self, cypher: str, params: dict | None = None):
        if not self.is_connected:
            return
        with self._driver.session() as session:
            session.run(cypher, params or {})


neo4j_client = Neo4jClient()
