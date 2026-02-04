"""MCP Server for AI Dev Graph - Model Context Protocol Interface.

This module provides a Model Context Protocol (MCP) server that allows AI agents
to interact with the knowledge graph through a standardized interface.

MCP enables:
- Reading graph structure and node content
- Querying relationships and dependencies
- Getting context for code generation
- Validating knowledge consistency
"""

import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from ai_dev_graph.core.graph import KnowledgeGraph, NodeType
from ai_dev_graph.models.manager import GraphManager

logger = logging.getLogger(__name__)


class MCPServer:
    """MCP Server for AI Dev Graph integration with language models."""
    
    def __init__(self, graph_manager: GraphManager):
        """Initialize MCP server with a graph manager.
        
        Args:
            graph_manager: GraphManager instance for graph operations.
        """
        self.graph_manager = graph_manager
        self.kg = graph_manager.load_or_create()
    
    def get_node(self, node_id: str) -> Dict[str, Any]:
        """Retrieve a single node with its context.
        
        Args:
            node_id: ID of the node to retrieve.
            
        Returns:
            Dictionary with node data and relationships.
        """
        context = self.kg.get_context(node_id, depth=2)
        if not context:
            return {"error": f"Node '{node_id}' not found"}
        return context
    
    def search_nodes(self, query: str, node_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for nodes by content and optionally filter by type.
        
        Args:
            query: Search query string.
            node_type: Optional NodeType to filter results.
            
        Returns:
            List of matching nodes with their content.
        """
        filters = {"content_match": query}
        if node_type:
            filters["type"] = node_type
        
        node_ids = self.kg.find_nodes(**filters)
        results = []
        
        for node_id in node_ids:
            node_data = self.kg.graph.nodes[node_id].get("data", {})
            results.append({
                "id": node_id,
                "type": node_data.get("type"),
                "content": node_data.get("content"),
            })
        
        return results
    
    def get_graph_structure(self) -> Dict[str, Any]:
        """Get the complete graph structure optimized for AI context.
        
        Returns:
            Dictionary with graph topology and statistics.
        """
        stats = self.kg.get_graph_stats()
        
        # Build adjacency information
        nodes = []
        edges = []
        
        for node_id, node_attrs in self.kg.graph.nodes(data=True):
            node_data = node_attrs.get("data", {})
            nodes.append({
                "id": node_id,
                "type": node_data.get("type"),
                "content": node_data.get("content", ""),
            })
        
        for source, target in self.kg.graph.edges():
            edges.append({"from": source, "to": target})
        
        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "total_nodes": stats.get("total_nodes", 0),
                "total_edges": stats.get("total_edges", 0),
                "density": stats.get("density", 0),
                "node_types": stats.get("node_type_distribution", {}),
            }
        }
    
    def get_context_for_node(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get full context for a node including ancestors and descendants.
        
        Args:
            node_id: ID of the node.
            depth: Depth of context traversal.
            
        Returns:
            Dictionary with comprehensive context.
        """
        return self.kg.get_context(node_id, depth=depth)
    
    def validate_graph(self) -> Dict[str, Any]:
        """Validate graph integrity and consistency.
        
        Returns:
            Validation report with any issues found.
        """
        return self.graph_manager.validate_graph()
    
    def export_for_agent(self) -> str:
        """Export graph in optimized format for AI agent consumption.
        
        Returns:
            JSON string with optimized graph representation.
        """
        graph_data = self.get_graph_structure()
        return json.dumps(graph_data, indent=2, ensure_ascii=False)
    
    def get_rules_and_standards(self) -> List[Dict[str, Any]]:
        """Get all rules and guidelines from the graph.
        
        Useful for agents to understand project constraints and standards.
        
        Returns:
            List of rule and guideline nodes.
        """
        rules = self.kg.find_nodes(type=NodeType.RULE)
        guidelines = self.kg.find_nodes(type=NodeType.GUIDELINE)
        
        results = []
        for node_id in rules + guidelines:
            node_data = self.kg.graph.nodes[node_id].get("data", {})
            results.append({
                "id": node_id,
                "type": node_data.get("type"),
                "content": node_data.get("content"),
            })
        
        return results
    
    def get_project_overview(self) -> Dict[str, Any]:
        """Get high-level project overview from the graph.
        
        Returns:
            Dictionary with project structure and key information.
        """
        # Get root project node
        project_nodes = self.kg.find_nodes(type=NodeType.PROJECT)
        
        overview = {
            "projects": [],
            "total_nodes": self.kg.graph.number_of_nodes(),
            "total_edges": self.kg.graph.number_of_edges(),
        }
        
        for proj_id in project_nodes:
            proj_data = self.kg.graph.nodes[proj_id].get("data", {})
            context = self.kg.get_context(proj_id, depth=1)
            
            overview["projects"].append({
                "id": proj_id,
                "content": proj_data.get("content"),
                "children": context.get("children", []),
            })
        
        return overview


def create_mcp_server(storage_dir: str = "graphs") -> MCPServer:
    """Factory function to create and initialize an MCP server.
    
    Args:
        storage_dir: Directory for graph storage.
        
    Returns:
        Initialized MCPServer instance.
    """
    graph_manager = GraphManager(storage_dir=storage_dir)
    return MCPServer(graph_manager)
