import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from ai_dev_graph.core.graph import KnowledgeGraph
from ai_dev_graph.init_meta_graph import init_project_graph

logger = logging.getLogger(__name__)

DEFAULT_GRAPH_FILENAME = "v0_initial.json"

class GraphManager:
    """
    Manages the lifecycle of the knowledge graph: loading, saving, backups,
    and validation.
    """
    
    def __init__(self, storage_dir: str = "graphs", use_db: bool = True):
        """Initialize GraphManager with optional database persistence.
        
        Args:
            storage_dir: Directory for JSON backups.
            use_db: Enable SQLite database persistence (default: True).
        """
        self.storage_dir = Path(storage_dir).resolve()
        self.current_graph: Optional[KnowledgeGraph] = None
        self.graph_path = self.storage_dir / DEFAULT_GRAPH_FILENAME
        self.use_db = use_db
        
        # Ensure storage directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def load_or_create(self) -> KnowledgeGraph:
        """Load existing graph from database or create a new one if not found."""
        kg = KnowledgeGraph(use_db=self.use_db)
        
        # If database is empty and JSON exists, migrate from JSON
        if self.use_db and kg.graph.number_of_nodes() == 0 and self.graph_path.exists():
            logger.info(f"Migrating graph from JSON: {self.graph_path}")
            temp_kg = KnowledgeGraph(use_db=False)
            temp_kg.load(str(self.graph_path))
            
            # Migrate all nodes and edges to database
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
            
            # Reload from DB
            kg._load_from_db()
            logger.info("Migration complete")
        
        # If still empty, initialize
        elif kg.graph.number_of_nodes() == 0:
            logger.info("Initializing new graph")
            kg = init_project_graph(storage_dir=str(self.storage_dir))
        else:
            logger.info(f"Graph loaded from database with {kg.graph.number_of_nodes()} nodes")
        
        self.current_graph = kg
        return self.current_graph

    def save_with_backup(self) -> bool:
        """Save current graph and create a timestamped backup."""
        if not self.current_graph:
            logger.warning("No graph to save.")
            return False

        try:
            # 1. Create backup if file exists
            if self.graph_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"v0_initial_backup_{timestamp}.json"
                backup_path = self.storage_dir / backup_name
                shutil.copy2(self.graph_path, backup_path)
                logger.info(f"Backup created: {backup_path}")

            # 2. Save current graph
            self.current_graph.save(str(self.graph_path))
            logger.info(f"Graph saved to {self.graph_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving graph: {e}")
            return False

    def validate_graph(self) -> Dict[str, Any]:
        """Validate graph integrity."""
        if not self.current_graph:
            return {"valid": False, "error": "No graph loaded", "issues": ["No graph loaded"]}
            
        stats = self.current_graph.get_graph_stats()
        
        issues = []
        if stats["total_nodes"] == 0:
            issues.append("El grafo está vacío.")
        
        return {
            "valid": len(issues) == 0,
            "total_nodes": stats["total_nodes"],
            "total_edges": stats["total_edges"],
            "density": stats["density"],
            "issues": issues
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics and recommendations."""
        if not self.current_graph:
            return {}
            
        stats = self.current_graph.get_graph_stats()
        stats["recommendations"] = self.get_recommendations()
        return stats

    def get_recommendations(self) -> List[str]:
        """Generate intelligent recommendations based on graph state."""
        recommendations = []
        if not self.current_graph:
            return recommendations
            
        stats = self.current_graph.get_graph_stats()
        
        if stats["total_nodes"] < 5:
            recommendations.append("El grafo es pequeño. Considera añadir más conceptos clave.")
            
        return recommendations

    def export_for_agent(self, agent_type: str) -> Dict[str, Any]:
        """Export graph data optimized for a specific agent."""
        if not self.current_graph:
            return {}
            
        stats = self.current_graph.get_graph_stats()
        
        return {
            "export_date": datetime.now().isoformat(),
            "agent_type": agent_type,
            "statistics": stats,
            "nodes_by_type": stats.get("node_types", {})
        }


def get_graph_manager(storage_dir: str = "graphs", use_db: bool = True) -> GraphManager:
    """Factory function to get a GraphManager instance.
    
    Args:
        storage_dir: Directory for graph storage.
        use_db: Enable database persistence.
        
    Returns:
        GraphManager instance.
    """
    return GraphManager(storage_dir=storage_dir, use_db=use_db)
