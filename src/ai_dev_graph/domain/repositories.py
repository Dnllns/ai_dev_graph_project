from typing import Protocol, List, Dict, Any, Optional, Tuple
from ai_dev_graph.domain.models import NodeData


class GraphRepository(Protocol):
    """Protocol for graph persistence and retrieval."""

    def add_node(self, node: NodeData) -> None:
        """Add a node to the graph."""
        ...

    def add_edge(self, source_id: str, target_id: str) -> None:
        """Add an edge between two nodes."""
        ...

    def get_node(self, node_id: str) -> Optional[NodeData]:
        """Retrieve a node by its ID."""
        ...

    def get_all_nodes(self) -> List[NodeData]:
        """Retrieve all nodes in the graph."""
        ...

    def get_all_edges(self) -> List[Tuple[str, str]]:
        """Retrieve all edges in the graph."""
        ...

    def update_node(
        self,
        node_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update node content or metadata."""
        ...

    def delete_node(self, node_id: str) -> bool:
        """Delete a node and its associated edges."""
        ...

    def find_nodes(self, **filters) -> List[str]:
        """Search for nodes based on filters."""
        ...

    def get_neighbors(self, node_id: str) -> Dict[str, List[str]]:
        """Get parents and children of a node."""
        ...

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        ...
