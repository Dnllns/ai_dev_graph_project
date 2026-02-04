import networkx as nx
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from enum import Enum
from ai_dev_graph.core.persistence import GraphDatabase


class NodeType(str, Enum):
    PROJECT = "project"       # Nodo raíz
    CONCEPT = "concept"       # Ideas abstractas o filosofías
    RULE = "rule"             # Obligatorio (MUST)
    GUIDELINE = "guideline"   # Recomendado (SHOULD)
    INSTRUCTION = "instruction" # Tarea específica
    RESOURCE = "resource"     # Archivos, herramientas
    TEST = "test"             # Criterios de validación

class NodeData(BaseModel):
    id: str
    type: NodeType
    content: str
    metadata: Dict[str, Any] = {}

class KnowledgeGraph:
    def __init__(self, use_db: bool = True, db_path: str = "data/graph.db"):
        """Initialize knowledge graph with optional database persistence.
        
        Args:
            use_db: Enable database persistence (default: True).
            db_path: Path to SQLite database file.
        """
        self.graph = nx.DiGraph()
        self.use_db = use_db
        self.db: Optional[GraphDatabase] = None
        
        if use_db:
            self.db = GraphDatabase(db_path)
            self._load_from_db()
    
    def _load_from_db(self):
        """Load graph from database into NetworkX."""
        if not self.db:
            return
        
        # Load all nodes
        for node_data in self.db.get_all_nodes():
            self.graph.add_node(node_data["id"], data={
                "id": node_data["id"],
                "type": node_data["type"],
                "content": node_data["content"],
                "metadata": node_data["metadata"]
            })
        
        # Load all edges
        for source, target in self.db.get_all_edges():
            self.graph.add_edge(source, target)


    def add_knowledge(self, node: NodeData, parents: List[str] = []):
        """Add a node to the graph with optional parent relationships.
        
        Args:
            node: NodeData object containing node information.
            parents: List of parent node IDs.
        """
        # Add to NetworkX
        self.graph.add_node(node.id, data=node.model_dump())
        for parent in parents:
            if self.graph.has_node(parent):
                self.graph.add_edge(parent, node.id)
        
        # Persist to database
        if self.db:
            self.db.add_node(
                node_id=node.id,
                node_type=node.type.value,
                content=node.content,
                metadata=node.metadata
            )
            for parent in parents:
                if self.graph.has_node(parent):
                    self.db.add_edge(parent, node.id)


    def get_context(self, node_id: str, depth: int = 1) -> Dict[str, Any]:
        """Recuperar contexto de un nodo: padres, hijos y metadatos.
        
        Args:
            node_id: ID del nodo central
            depth: Profundidad de búsqueda en el grafo
            
        Returns:
            Diccionario con el contexto (padres, hijos, datos del nodo)
        """
        if not self.graph.has_node(node_id):
            return {}
        
        context = {
            "node": self.graph.nodes[node_id],
            "parents": [],
            "children": [],
            "ancestors": [],
            "descendants": []
        }
        
        # Padres directos (predecessors)
        context["parents"] = list(self.graph.predecessors(node_id))
        
        # Hijos directos (successors)
        context["children"] = list(self.graph.successors(node_id))
        
        # Ancestros y descendientes si depth > 1
        if depth > 1:
            context["ancestors"] = list(nx.ancestors(self.graph, node_id))
            context["descendants"] = list(nx.descendants(self.graph, node_id))
        
        return context

    def find_nodes(self, **filters) -> List[str]:
        """Buscar nodos por criterios (type, contenido, etc).
        
        Args:
            **filters: Criterios de búsqueda (type=NodeType, content_match=str, etc)
            
        Returns:
            Lista de IDs de nodos que coinciden
        """
        results = []
        for node_id, attrs in self.graph.nodes(data=True):
            node_data = attrs.get("data", {})
            match = True
            
            # Filtrar por tipo
            if "type" in filters:
                if node_data.get("type") != filters["type"]:
                    match = False
            
            # Filtrar por contenido
            if "content_match" in filters and match:
                if filters["content_match"].lower() not in node_data.get("content", "").lower():
                    match = False
            
            if match:
                results.append(node_id)
        
        return results

    def get_graph_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del grafo.
        
        Returns:
            Diccionario con estadísticas del grafo
        """
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

    def update_node(self, node_id: str, content: str = None, metadata: Dict = None) -> bool:
        """Actualizar contenido o metadatos de un nodo.
        
        Args:
            node_id: ID del nodo
            content: Nuevo contenido (opcional)
            metadata: Nuevos metadatos (opcional)
            
        Returns:
            True si se actualizó exitosamente
        """
        if not self.graph.has_node(node_id):
            return False
        
        node_data = self.graph.nodes[node_id].get("data", {})
        
        if content is not None:
            node_data["content"] = content
        
        if metadata is not None:
            node_data["metadata"].update(metadata)
        
        self.graph.nodes[node_id]["data"] = node_data
        
        # Persist to database
        if self.db:
            self.db.update_node(node_id, content=content, metadata=metadata)
        
        return True

    def delete_node(self, node_id: str) -> bool:
        """Eliminar un nodo y sus aristas.
        
        Args:
            node_id: ID del nodo a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)
            
            # Persist to database
            if self.db:
                self.db.delete_node(node_id)
            
            return True
        return False

    def save(self, path: str):
        """Guardar el grafo a un archivo JSON.
        
        Args:
            path: Ruta de archivo de destino
        """
        data = nx.node_link_data(self.graph)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, path: str):
        """Cargar el grafo desde un archivo JSON.
        
        Args:
            path: Ruta del archivo a cargar
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.graph = nx.node_link_graph(data)
