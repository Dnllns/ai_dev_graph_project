"""Database persistence layer for the knowledge graph.

Uses SQLite to provide robust graph storage with ACID guarantees while
maintaining the simplicity of a file-based database.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class GraphDatabase:
    """SQLite-backed graph database for persistent storage."""
    
    def __init__(self, db_path: str = "data/graph.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create database schema if it doesn't exist."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Nodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Edges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source, target),
                FOREIGN KEY (source) REFERENCES nodes(id) ON DELETE CASCADE,
                FOREIGN KEY (target) REFERENCES nodes(id) ON DELETE CASCADE
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_node_type ON nodes(type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_edge_source ON edges(source)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_edge_target ON edges(target)
        """)
        
        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def add_node(self, node_id: str, node_type: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a node to the database.
        
        Args:
            node_id: Unique identifier for the node.
            node_type: Type of the node (project, concept, rule, etc).
            content: Node content/description.
            metadata: Optional metadata dictionary.
            
        Returns:
            True if node was added successfully.
        """
        try:
            cursor = self.conn.cursor()
            metadata_json = json.dumps(metadata or {})
            
            cursor.execute("""
                INSERT OR REPLACE INTO nodes (id, type, content, metadata, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (node_id, node_type, content, metadata_json))
            
            self.conn.commit()
            logger.debug(f"Added node: {node_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding node {node_id}: {e}")
            self.conn.rollback()
            return False
    
    def add_edge(self, source: str, target: str) -> bool:
        """Add an edge between two nodes.
        
        Args:
            source: Source node ID.
            target: Target node ID.
            
        Returns:
            True if edge was added successfully.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO edges (source, target)
                VALUES (?, ?)
            """, (source, target))
            
            self.conn.commit()
            logger.debug(f"Added edge: {source} -> {target}")
            return True
        except Exception as e:
            logger.error(f"Error adding edge {source}->{target}: {e}")
            self.conn.rollback()
            return False
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a node by ID.
        
        Args:
            node_id: ID of the node to retrieve.
            
        Returns:
            Node data dictionary or None if not found.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, type, content, metadata, created_at, updated_at
            FROM nodes WHERE id = ?
        """, (node_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "id": row["id"],
            "type": row["type"],
            "content": row["content"],
            "metadata": json.loads(row["metadata"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes from the database.
        
        Returns:
            List of all nodes.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, type, content, metadata, created_at, updated_at
            FROM nodes
            ORDER BY created_at
        """)
        
        nodes = []
        for row in cursor.fetchall():
            nodes.append({
                "id": row["id"],
                "type": row["type"],
                "content": row["content"],
                "metadata": json.loads(row["metadata"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })
        
        return nodes
    
    def get_all_edges(self) -> List[Tuple[str, str]]:
        """Get all edges from the database.
        
        Returns:
            List of (source, target) tuples.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT source, target FROM edges")
        return [(row["source"], row["target"]) for row in cursor.fetchall()]
    
    def update_node(self, node_id: str, content: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Update a node's content or metadata.
        
        Args:
            node_id: ID of the node to update.
            content: New content (if provided).
            metadata: New metadata (if provided).
            
        Returns:
            True if update was successful.
        """
        try:
            existing = self.get_node(node_id)
            if not existing:
                return False
            
            cursor = self.conn.cursor()
            
            if content is not None:
                cursor.execute("""
                    UPDATE nodes SET content = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (content, node_id))
            
            if metadata is not None:
                # Merge with existing metadata
                current_meta = existing["metadata"]
                current_meta.update(metadata)
                metadata_json = json.dumps(current_meta)
                
                cursor.execute("""
                    UPDATE nodes SET metadata = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (metadata_json, node_id))
            
            self.conn.commit()
            logger.debug(f"Updated node: {node_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating node {node_id}: {e}")
            self.conn.rollback()
            return False
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a node and all its edges.
        
        Args:
            node_id: ID of the node to delete.
            
        Returns:
            True if deletion was successful.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
            self.conn.commit()
            logger.debug(f"Deleted node: {node_id}")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting node {node_id}: {e}")
            self.conn.rollback()
            return False
    
    def find_nodes(self, node_type: str = None, content_match: str = None) -> List[str]:
        """Find nodes by type or content.
        
        Args:
            node_type: Filter by node type.
            content_match: Search in content (case-insensitive).
            
        Returns:
            List of node IDs matching the criteria.
        """
        cursor = self.conn.cursor()
        query = "SELECT id FROM nodes WHERE 1=1"
        params = []
        
        if node_type:
            query += " AND type = ?"
            params.append(node_type)
        
        if content_match:
            query += " AND content LIKE ?"
            params.append(f"%{content_match}%")
        
        cursor.execute(query, params)
        return [row["id"] for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with node and edge counts.
        """
        cursor = self.conn.cursor()
        
        # Node count
        cursor.execute("SELECT COUNT(*) as count FROM nodes")
        node_count = cursor.fetchone()["count"]
        
        # Edge count
        cursor.execute("SELECT COUNT(*) as count FROM edges")
        edge_count = cursor.fetchone()["count"]
        
        # Node types distribution
        cursor.execute("SELECT type, COUNT(*) as count FROM nodes GROUP BY type")
        node_types = {row["type"]: row["count"] for row in cursor.fetchall()}
        
        return {
            "total_nodes": node_count,
            "total_edges": edge_count,
            "node_types": node_types
        }
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
