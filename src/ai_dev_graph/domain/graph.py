from typing import List, Dict, Any, Optional
from ai_dev_graph.domain.models import NodeData
from ai_dev_graph.domain.repositories import GraphRepository

class KnowledgeGraph:
    """Domain logic for managing the knowledge graph.
    
    This class orchestrates business rules for the graph but remains
    agnostic of the actual persistence implementation (DIP).
    """
    
    def __init__(self, repository: GraphRepository):
        self.repo = repository
        
    def add_knowledge(self, node: NodeData, parents: List[str] = []):
        """Add a node to the graph with optional parent relationships."""
        self.repo.add_node(node)
        for parent in parents:
            self.repo.add_edge(parent, node.id)
            
    def get_context(self, node_id: str, depth: int = 1) -> Dict[str, Any]:
        """Recuperar contexto de un nodo: padres, hijos y metadatos."""
        node = self.repo.get_node(node_id)
        if not node:
            return {}
            
        neighbors = self.repo.get_neighbors(node_id)
        
        context = {
            "node": node.model_dump(),
            "parents": neighbors.get("parents", []),
            "children": neighbors.get("children", []),
            "ancestors": [], 
            "descendants": []
        }
        
        return context

    def find_nodes(self, **filters) -> List[str]:
        """Buscar nodos por criterios."""
        return self.repo.find_nodes(**filters)

    def get_graph_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del grafo."""
        return self.repo.get_stats()

    def update_node(self, node_id: str, content: str = None, metadata: Dict = None) -> bool:
        """Actualizar contenido o metadatos de un nodo."""
        return self.repo.update_node(node_id, content=content, metadata=metadata)

    def delete_node(self, node_id: str) -> bool:
        """Eliminar un nodo y sus aristas."""
        return self.repo.delete_node(node_id)

    def has_node(self, node_id: str) -> bool:
        """Check if a node exists in the graph."""
        return self.repo.get_node(node_id) is not None

    def get_node_data(self, node_id: str) -> Optional[NodeData]:
        """Get data for a specific node."""
        return self.repo.get_node(node_id)

    def get_successors(self, node_id: str) -> List[str]:
        """Get direct children of a node."""
        return self.repo.get_neighbors(node_id).get("children", [])

    def get_predecessors(self, node_id: str) -> List[str]:
        """Get direct parents of a node."""
        return self.repo.get_neighbors(node_id).get("parents", [])
