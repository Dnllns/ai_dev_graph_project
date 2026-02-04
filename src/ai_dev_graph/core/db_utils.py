"""Database management utilities for the AI Dev Graph.

Provides CLI commands for database operations like backup, restore, and export.
"""

import shutil
from pathlib import Path
from datetime import datetime
import json
import logging

from ai_dev_graph.core.persistence import GraphDatabase
from ai_dev_graph.core.graph import KnowledgeGraph

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
    """Export database to JSON format.
    
    Args:
        db_path: Path to the database file.
        output_path: Output JSON file path.
    """
    kg = KnowledgeGraph(use_db=True, db_path=db_path)
    kg.save(output_path)
    logger.info(f"Graph exported to JSON: {output_path}")


def import_from_json(json_path: str, db_path: str = "data/graph.db", clear_existing: bool = False):
    """Import graph from JSON into database.
    
    Args:
        json_path: Path to JSON file.
        db_path: Path to database file.
        clear_existing: If True, clear existing data before import.
    """
    if clear_existing:
        logger.warning("Clearing existing database...")
        db_file = Path(db_path)
        if db_file.exists():
            db_file.unlink()
    
    # Load from JSON
    temp_kg = KnowledgeGraph(use_db=False)
    temp_kg.load(json_path)
    
    # Create new DB-backed graph
    kg = KnowledgeGraph(use_db=True, db_path=db_path)
    
    # Import all nodes and edges
    for node_id, attrs in temp_kg.graph.nodes(data=True):
        node_data = attrs.get("data", {})
        kg.db.add_node(
            node_id=node_data["id"],
            node_type=node_data["type"],
            content=node_data["content"],
            metadata=node_data.get("metadata", {})
        )
    
    for source, target in temp_kg.graph.edges():
        kg.db.add_edge(source, target)
    
    logger.info(f"Imported {temp_kg.graph.number_of_nodes()} nodes from {json_path}")


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
