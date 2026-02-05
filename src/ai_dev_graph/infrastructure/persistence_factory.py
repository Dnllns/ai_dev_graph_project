from typing import Optional
from ai_dev_graph.domain.repositories import GraphRepository
from ai_dev_graph.core.config import settings, DatabaseType
from ai_dev_graph.infrastructure.networkx_repo import NetworkXSQLiteRepository
from ai_dev_graph.infrastructure.neo4j_repo import Neo4jRepository
from ai_dev_graph.infrastructure.hybrid_repo import HybridRepository
import logging

logger = logging.getLogger(__name__)

_repository_instance: Optional[GraphRepository] = None

class PersistenceFactory:
    """Factory for creating graph repository instances based on configuration."""
    
    @staticmethod
    def get_repository() -> GraphRepository:
        global _repository_instance
        if _repository_instance is None:
            db_type = settings.database_type
            logger.info(f"Initializing repository for database type: {db_type}")
            
            if db_type == DatabaseType.NEO4J:
                try:
                    _repository_instance = Neo4jRepository()
                except Exception as e:
                    logger.error(f"Failed to initialize Neo4j repository: {e}")
                    raise e
            elif db_type == DatabaseType.HYBRID:
                try:
                    _repository_instance = HybridRepository()
                except Exception as e:
                    logger.error(f"Failed to initialize Hybrid repository: {e}")
                    raise e
            elif db_type == DatabaseType.SQLITE:
                _repository_instance = NetworkXSQLiteRepository()
            else:
                # Default/Fallback
                logger.warning(f"Unknown database type {db_type}, defaulting to SQLite")
                _repository_instance = NetworkXSQLiteRepository()
                
        return _repository_instance
    
    @staticmethod
    def reset():
        """Reset the singleton instance (useful for tests)."""
        global _repository_instance
        if _repository_instance and hasattr(_repository_instance, 'close'):
            try:
                _repository_instance.close()
            except Exception:
                pass
        _repository_instance = None
