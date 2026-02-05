"""Database management utilities for the AI Dev Graph.

Provides CLI commands for database operations like backup, restore, and export.
"""

import shutil
from pathlib import Path
from datetime import datetime
import json
import logging

from ai_dev_graph.core.persistence import GraphDatabase
from ai_dev_graph.domain.graph import KnowledgeGraph
from ai_dev_graph.infrastructure.networkx_repo import NetworkXSQLiteRepository

logger = logging.getLogger(__name__)


def backup_database(db_path: str = "data/graph.db", backup_dir: str = "data/backups") -> str:
    """Create a timestamped backup of the database.
    
    Args:
        db_path: Path to the database file.
        backup_dir: Directory to store backups.
        
    Returns:
        Path to the backup file.
    """
    db_file = Path(db_path)
    if not db_file.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_path / f"graph_backup_{timestamp}.db"
    
    shutil.copy2(db_file, backup_file)
    logger.info(f"Database backed up to: {backup_file}")
    
    return str(backup_file)


def export_to_json(db_path: str = "data/graph.db", output_path: str = "graphs/export.json"):
    """Export database to JSON format."""
    repo = NetworkXSQLiteRepository(db_path=db_path)
    # Use networkx format for export
    import networkx as nx
    data = nx.node_link_data(repo.graph)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Graph exported to JSON: {output_path}")


def import_from_json(json_path: str, db_path: str = "data/graph.db", clear_existing: bool = False):
    """Import graph from JSON into database."""
    if clear_existing:
        logger.warning("Clearing existing database...")
        db_file = Path(db_path)
        if db_file.exists():
            db_file.unlink()
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    import networkx as nx
    temp_graph = nx.node_link_graph(data)
    
    # Create new DB-backed graph
    repo = NetworkXSQLiteRepository(db_path=db_path)
    kg = KnowledgeGraph(repository=repo)
    
    from ai_dev_graph.domain.models import NodeData, NodeType
    
    # Import all nodes and edges
    for node_id, attrs in temp_graph.nodes(data=True):
        node_data = attrs.get("data", {})
        if not node_data:
            # Fallback for old formats
            node_data = {
                "id": node_id,
                "type": attrs.get("type", "concept"),
                "content": attrs.get("content", ""),
                "metadata": attrs.get("metadata", {})
            }
            
        node = NodeData(**node_data)
        kg.repo.add_node(node)
    
    for source, target in temp_graph.edges():
        kg.repo.add_edge(source, target)
    
    logger.info(f"Imported nodes from {json_path}")


def get_db_info(db_path: str = "data/graph.db") -> dict:
    """Get database statistics and info.
    
    Args:
        db_path: Path to database file.
        
    Returns:
        Dictionary with database information.
    """
    db_file = Path(db_path)
    
    if not db_file.exists():
        return {"exists": False, "error": "Database file not found"}
    
    db = GraphDatabase(db_path)
    stats = db.get_statistics()
    
    file_size = db_file.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    
    return {
        "exists": True,
        "path": str(db_file.absolute()),
        "size_bytes": file_size,
        "size_mb": round(file_size_mb, 2),
        **stats
    }
