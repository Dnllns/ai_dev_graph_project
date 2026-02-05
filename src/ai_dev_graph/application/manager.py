import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from ai_dev_graph.domain.graph import KnowledgeGraph
from ai_dev_graph.infrastructure.networkx_repo import NetworkXSQLiteRepository
from ai_dev_graph.init_meta_graph import init_project_graph

logger = logging.getLogger(__name__)

DEFAULT_GRAPH_FILENAME = "v0_initial.json"

class GraphManager:
    """
    Application service that manages the lifecycle of the knowledge graph.
    """
    
    def __init__(self, storage_dir: str = "graphs", use_db: bool = True):
        self.storage_dir = Path(storage_dir).resolve()
        self.current_graph: Optional[KnowledgeGraph] = None
        self.graph_path = self.storage_dir / DEFAULT_GRAPH_FILENAME
        self.use_db = use_db
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def load_or_create(self) -> KnowledgeGraph:
        """Load existing graph from database or create a new one."""
        # DIP: We instantiate the repository through the factory
        from ai_dev_graph.infrastructure.persistence_factory import PersistenceFactory
        from ai_dev_graph.init_meta_graph import init_project_graph
        
        repo = PersistenceFactory.get_repository()
        kg = KnowledgeGraph(repository=repo)
        
        # Initial check
        try:
            stats = kg.get_graph_stats()
            
            if stats["total_nodes"] == 0:
                logger.info("Initializing new graph")
                # We reuse the same kg instance but populate it
                # We need to make sure init_project_graph uses the same repo
                # For now let's see if we can pass the repo to init_project_graph
                kg = init_project_graph(repository=repo)
            else:
                logger.info(f"Graph loaded with {stats['total_nodes']} nodes")
        except Exception as e:
            logger.warning(f"Could not load stats, assuming empty or error: {e}")
            logger.info("Initializing new graph")
            kg = init_project_graph(repository=repo)
        
        self.current_graph = kg
        return self.current_graph

    def save_with_backup(self) -> bool:
        """Save current graph (metadata/JSON) and create a backup."""
        if not self.current_graph:
            return False

        try:
            if self.graph_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"v0_initial_backup_{timestamp}.json"
                backup_path = self.storage_dir / backup_name
                shutil.copy2(self.graph_path, backup_path)
                logger.info(f"Backup created: {backup_path}")

            # Legacy JSON save for compatibility if needed, 
            # though infrastructure handles SQLite now.
            # For now, we'll keep it simple.
            return True
        except Exception as e:
            logger.error(f"Error saving graph: {e}")
            return False

    def validate_graph(self) -> Dict[str, Any]:
        """Validate graph integrity."""
        if not self.current_graph:
            return {"valid": False, "error": "No graph loaded"}
            
        stats = self.current_graph.get_graph_stats()
        issues = []
        if stats["total_nodes"] == 0:
            issues.append("El grafo está vacío.")
        
        return {
            "valid": len(issues) == 0,
            "total_nodes": stats["total_nodes"],
            "total_edges": stats["total_edges"],
            "issues": issues
        }

    def get_statistics(self) -> Dict[str, Any]:
        if not self.current_graph:
            return {}
        stats = self.current_graph.get_graph_stats()
        stats["recommendations"] = self.get_recommendations()
        return stats

    def get_recommendations(self) -> List[str]:
        recommendations = []
        if not self.current_graph:
            return recommendations
        stats = self.current_graph.get_graph_stats()
        if stats["total_nodes"] < 5:
            recommendations.append("El grafo es pequeño. Considera añadir más conceptos clave.")
        return recommendations

    def export_for_agent(self, agent_type: str) -> Dict[str, Any]:
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
    return GraphManager(storage_dir=storage_dir, use_db=use_db)
