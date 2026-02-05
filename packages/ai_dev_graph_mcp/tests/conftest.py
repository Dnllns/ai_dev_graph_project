import os
import pytest
import tempfile
from ai_dev_graph.core.config import settings, DatabaseType
from ai_dev_graph_mcp.server import GraphManager

# Force PersistenceFactory reset via GraphManager if accessible, or re-import
from ai_dev_graph.infrastructure.persistence_factory import PersistenceFactory


@pytest.fixture(autouse=True)
def force_test_db():
    """Force SQLite and use temp DB for all tests to ensure isolation."""
    # Store original settings
    original_type = settings.database_type
    original_path = settings.sqlite_path

    # Create temp DB file
    tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp_db.close()

    # Override settings
    settings.database_type = DatabaseType.SQLITE
    settings.sqlite_path = tmp_db.name

    # Reset factory to pick up new settings
    PersistenceFactory.reset()

    yield

    # Cleanup file
    if os.path.exists(tmp_db.name):
        try:
            os.remove(tmp_db.name)
        except OSError:
            pass

    # Restore settings
    settings.database_type = original_type
    settings.sqlite_path = original_path
    PersistenceFactory.reset()
