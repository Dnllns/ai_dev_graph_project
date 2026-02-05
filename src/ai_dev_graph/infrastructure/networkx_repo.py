import networkx as nx
from typing import List, Dict, Any, Optional, Tuple
from ai_dev_graph.domain.models import NodeData
from ai_dev_graph.core.persistence import GraphDatabase

from ai_dev_graph.core.config import settings

class NetworkXSQLiteRepository:
    """Infrastructure implementation using NetworkX for graph logic and SQLite for persistence."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.sqlite_path
        self.graph = nx.DiGraph()
        self.db = GraphDatabase(self.db_path)
        self._load_from_db()
        
    def _load_from_db(self):
        """Sync DB to memory."""
        for node_data in self.db.get_all_nodes():
            self.graph.add_node(node_data["id"], data=node_data)
            
        for source, target in self.db.get_all_edges():
            self.graph.add_edge(source, target)
            
    def add_node(self, node: NodeData) -> None:
        self.graph.add_node(node.id, data=node.model_dump())
        self.db.add_node(
            node_id=node.id,
            node_type=node.type.value,
            content=node.content,
            metadata=node.metadata
        )
        
    def add_edge(self, source_id: str, target_id: str) -> None:
        if self.graph.has_node(source_id) and self.graph.has_node(target_id):
            self.graph.add_edge(source_id, target_id)
            self.db.add_edge(source_id, target_id)
            
    def get_node(self, node_id: str) -> Optional[NodeData]:
        if not self.graph.has_node(node_id):
            return None
        data = self.graph.nodes[node_id].get("data")
        if not data:
            return None
        return NodeData(**data)
        
    def get_all_nodes(self) -> List[NodeData]:
        nodes = []
        for node_id, attrs in self.graph.nodes(data=True):
            data = attrs.get("data")
            if data:
                nodes.append(NodeData(**data))
        return nodes
        
    def get_all_edges(self) -> List[Tuple[str, str]]:
        return list(self.graph.edges())
        
    def update_node(self, node_id: str, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        if not self.graph.has_node(node_id):
            return False
            
        node_data = self.graph.nodes[node_id].get("data", {})
        if content is not None:
            node_data["content"] = content
        if metadata is not None:
            if "metadata" not in node_data:
                node_data["metadata"] = {}
            node_data["metadata"].update(metadata)
            
        self.graph.nodes[node_id]["data"] = node_data
        self.db.update_node(node_id, content=content, metadata=metadata)
        return True
        
    def delete_node(self, node_id: str) -> bool:
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)
            self.db.delete_node(node_id)
            return True
        return False
        
    def find_nodes(self, **filters) -> List[str]:
        results = []
        for node_id, attrs in self.graph.nodes(data=True):
            node_data = attrs.get("data", {})
            match = True
            
            if "type" in filters:
                if node_data.get("type") != filters["type"]:
                    match = False
            
            if "content_match" in filters and match:
                if filters["content_match"].lower() not in node_data.get("content", "").lower():
                    match = False
                    
            if match:
                results.append(node_id)
        return results
        
    def get_neighbors(self, node_id: str) -> Dict[str, List[str]]:
        if not self.graph.has_node(node_id):
            return {}
        return {
            "parents": list(self.graph.predecessors(node_id)),
            "children": list(self.graph.successors(node_id))
        }
        
    def get_stats(self) -> Dict[str, Any]:
        node_types = {}
        for node_id, attrs in self.graph.nodes(data=True):
            node_type = attrs.get("data", {}).get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
            
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": node_types,
            "density": nx.density(self.graph)
        }
