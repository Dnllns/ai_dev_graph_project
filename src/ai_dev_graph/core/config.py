from enum import Enum
import os
from pydantic import BaseModel


class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    NEO4J = "neo4j"
    HYBRID = "hybrid"  # Neo4j for structure, SQLite for metadata
    MEMORY = "memory"


class Settings(BaseModel):
    # Core settings
    database_type: DatabaseType = DatabaseType(os.getenv("DATABASE_TYPE", "hybrid"))

    # Neo4j settings
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    neo4j_db: str = os.getenv("NEO4J_DB", "neo4j")

    # SQLite settings
    sqlite_path: str = os.getenv("SQLITE_PATH", "data/graph.db")


settings = Settings()
