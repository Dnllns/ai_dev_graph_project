from typing import List, Dict, Any, Optional, Tuple
import json
import logging
from ai_dev_graph.domain.models import NodeData, NodeType
from ai_dev_graph.domain.repositories import GraphRepository
from ai_dev_graph.infrastructure.neo4j_repo import Neo4jRepository
from ai_dev_graph.core.persistence import GraphDatabase
from ai_dev_graph.core.config import settings

logger = logging.getLogger(__name__)

class HybridRepository(GraphRepository):
    """
    Hybrid repository implementation that uses:
    - Neo4j for graph structure (efficient traversal, relationships).
    - SQLite for node content and metadata (cost-effective storage).
    
    This implements Polyglot Persistence.
    """
    
    def __init__(self):
        logger.info("Initializing Hybrid Repository (Neo4j + SQLite)")
        # Structure component
        self.neo4j = Neo4jRepository()
        
        # Content/Metadata component
        # We reuse the GraphDatabase class for SQLite interactions
        self.sqlite = GraphDatabase(db_path=settings.sqlite_path)
        
    def add_node(self, node: NodeData) -> None:
        """
        Dual write:
        1. Write full content/metadata to SQLite.
        2. Write structure (ID, Type) to Neo4j.
        """
        # 1. SQLite (Full payload)
        self.sqlite.add_node(
            node_id=node.id, 
            node_type=node.type.value,
            content=node.content,
            metadata=node.metadata
        )
        
        # 2. Neo4j (Structure only)
        # We create a lightweight NodeData for Neo4j to avoid sending huge blobs
        # although Neo4jRepository usually extracts everything. 
        # But we want to ensure Neo4j has at least ID and Type.
        self.neo4j.add_node(node)
        
    def add_edge(self, source_id: str, target_id: str) -> None:
        """Add edge to Neo4j (Primary for structure)."""
        # We also mirror it to SQLite for backup/consistency if desired, 
        # but Neo4j is the authority for relationships.
        # Let's mirror it to keep SQLite as a full backup if needed.
        self.neo4j.add_edge(source_id, target_id)
        self.sqlite.add_edge(source_id, target_id)
        
    def get_node(self, node_id: str) -> Optional[NodeData]:
        """
        Hybrid Read:
        1. Check Neo4j for existence (fast graph lookup) - Optional optimization.
        2. Fetch Heavy Data from SQLite.
        """
        # We trust SQLite for the content.
        row = self.sqlite.get_node(node_id)
        if not row:
            # If not in SQLite, check Neo4j just in case of desync?
            # For now, SQLite is the source of truth for "Data".
            return None
        
        return NodeData(
            id=row["id"],
            type=NodeType(row["type"]),
            content=row["content"],
            metadata=row["metadata"]
        )
        
    def get_all_nodes(self) -> List[NodeData]:
        """Get all nodes from SQLite (it has the data)."""
        rows = self.sqlite.get_all_nodes()
        return [
            NodeData(
                id=r["id"],
                type=NodeType(r["type"]),
                content=r["content"],
                metadata=r["metadata"]
            ) 
            for r in rows
        ]
        
    def get_all_edges(self) -> List[Tuple[str, str]]:
        """Get all edges from Neo4j (Authority for structure)."""
        return self.neo4j.get_all_edges()
        
    def update_node(self, node_id: str, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update node in SQLite (Content) and Neo4j (Metadata if searchable)."""
        # Update SQLite
        success = self.sqlite.update_node(node_id, content, metadata)
        
        # Sync to Neo4j if metadata changed (maybe useful for filtering?)
        # For this iteration, we treat Neo4j mainly for structure. 
        # If we filter by metadata in Neo4j, we should update it there too.
        if success:
            # Re-fetch full updated node to sync
            updated_node = self.get_node(node_id)
            if updated_node:
                self.neo4j.add_node(updated_node)
                
        return success
        
    def delete_node(self, node_id: str) -> bool:
        """Delete from both."""
        sq_del = self.sqlite.delete_node(node_id)
        ne_del = self.neo4j.delete_node(node_id)
        return sq_del or ne_del
        
    def find_nodes(self, **filters) -> List[str]:
        """
        Smart Search:
        - If filtering by 'content' (fulltext), use SQLite.
        - If filtering by 'type' only, use Neo4j or SQLite (SQLite is fine).
        - If filtering by complex graph patterns (future), use Neo4j.
        """
        # For now, delegate to SQLite for content search as it likely maps better 
        # to the current 'filters' implementation derived from SQLite repo.
        return self.sqlite.find_nodes(
            node_type=filters.get("type"),
            content_match=filters.get("content_match")
        )
        
    def get_neighbors(self, node_id: str) -> Dict[str, List[str]]:
        """
        Structure Query:
        - Use Neo4j to find parents/children IDs.
        """
        return self.neo4j.get_neighbors(node_id)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get combined stats."""
        # Nodes count from SQLite (data source)
        # Edges count from Neo4j (structure source)
        sq_stats = self.sqlite.get_statistics()
        ne_stats = self.neo4j.get_stats()
        
        return {
            "total_nodes": sq_stats["total_nodes"],
            "total_edges": ne_stats["total_edges"], # Neo4j is authority on edges
            "node_types": sq_stats["node_types"],
            "density": ne_stats.get("density", 0)
        }
