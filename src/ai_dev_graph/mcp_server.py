"""Enhanced MCP Server for AI Dev Graph - Model Context Protocol Interface.

This module provides an enhanced Model Context Protocol (MCP) server that allows AI agents
to interact with the knowledge graph through a standardized interface with advanced capabilities.

New Features:
- Waterfall methodology tracking integration
- Rule validation against graph
- Context-aware suggestions
- Agent workflow optimization
- Enhanced search with relevance scoring
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from ai_dev_graph.core.graph import KnowledgeGraph, NodeType
from ai_dev_graph.models.manager import GraphManager
from ai_dev_graph.waterfall_tracker import WaterfallTracker, WaterfallStage

logger = logging.getLogger(__name__)


class EnhancedMCPServer:
    """Enhanced MCP Server for AI Dev Graph integration with advanced agent capabilities."""
    
    def __init__(self, graph_manager: GraphManager):
        """Initialize enhanced MCP server with a graph manager.
        
        Args:
            graph_manager: GraphManager instance for graph operations.
        """
        self.graph_manager = graph_manager
        self.kg = graph_manager.load_or_create()
        self.waterfall = WaterfallTracker()
    
    # ===== CORE GRAPH OPERATIONS =====
    
    def get_node(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        """Retrieve a single node with its context.
        
        Args:
            node_id: ID of the node to retrieve.
            depth: Depth of context to include (default: 2).
            
        Returns:
            Dictionary with node data and relationships.
        """
        context = self.kg.get_context(node_id, depth=depth)
        if not context:
            return {"error": f"Node '{node_id}' not found"}
        return context
    
    def search_nodes(self, query: str, node_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for nodes by content with relevance scoring.
        
        Args:
            query: Search query string.
            node_type: Optional NodeType to filter results.
            limit: Maximum number of results (default: 10).
            
        Returns:
            List of matching nodes with relevance scores.
        """
        filters = {"content_match": query}
        if node_type:
            filters["type"] = node_type
        
        node_ids = self.kg.find_nodes(**filters)
        results = []
        
        for node_id in node_ids[:limit]:
            node_data = self.kg.graph.nodes[node_id].get("data", {})
            content = node_data.get("content", "")
            
            # Simple relevance scoring based on query matches
            relevance = content.lower().count(query.lower())
            
            results.append({
                "id": node_id,
                "type": node_data.get("type"),
                "content": content,
                "relevance": relevance,
                "parents": list(self.kg.graph.predecessors(node_id)),
                "children": list(self.kg.graph.successors(node_id))
            })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results
    
    # ===== WATERFALL METHODOLOGY =====
    
    def get_waterfall_stages(self) -> List[Dict[str, str]]:
        """Get all waterfall stages from the knowledge graph.
        
        Returns:
            List of stage definitions with their rules.
        """
        stages = []
        stage_nodes = [
            "stage_analysis", "stage_design", "stage_implementation",
            "stage_testing", "stage_documentation", "stage_release"
        ]
        
        for stage_id in stage_nodes:
            if self.kg.graph.has_node(stage_id):
                node_data = self.kg.graph.nodes[stage_id].get("data", {})
                stages.append({
                    "id": stage_id,
                    "name": stage_id.replace("stage_", "").upper(),
                    "description": node_data.get("content", "")
                })
        
        return stages
    
    def get_current_feature_context(self) -> Dict[str, Any]:
        """Get context for the currently active feature.
        
        Returns:
            Dictionary with current feature state and relevant graph nodes.
        """
        current = self.waterfall.get_current_feature()
        
        if not current:
            return {
                "status": "no_active_feature",
                "message": "No feature currently being tracked",
                "recommendation": "Start a new feature with: waterfall start <id> <title>"
            }
        
        # Get stage-specific guidance from graph
        stage_node_id = f"stage_{current.current_stage.value}"
        stage_guidance = {}
        
        if self.kg.graph.has_node(stage_node_id):
            stage_data = self.kg.graph.nodes[stage_node_id].get("data", {})
            stage_guidance = {
                "stage": current.current_stage.value,
                "guidance": stage_data.get("content", ""),
                "type": "rule"
            }
        
        return {
            "status": "active",
            "feature_id": current.feature_id,
            "title": current.title,
            "current_stage": current.current_stage.value,
            "started_at": current.started_at,
            "updated_at": current.updated_at,
            "completed_stages": [h["stage"] for h in current.stage_history],
            "stage_guidance": stage_guidance,
            "notes": current.notes
        }
    
    def validate_against_rules(self, action: str, context: dict = None) -> Dict[str, Any]:
        """Validate a proposed action against graph rules.
        
        Args:
            action: Description of the action to validate.
            context: Optional context dictionary.
            
        Returns:
            Validation result with applicable rules.
        """
        # Get all rules from graph
        rule_nodes = self.kg.find_nodes(type="rule")
        applicable_rules = []
        violations = []
        
        for rule_id in rule_nodes:
            rule_data = self.kg.graph.nodes[rule_id].get("data", {})
            rule_content = rule_data.get("content", "").lower()
            
            # Check if rule is relevant to action
            action_lower = action.lower()
            
            # Check for specific rule violations
            if "rule_no_skip_stages" in rule_id and "skip" in action_lower:
                violations.append({
                    "rule": rule_id,
                    "severity": "error",
                    "message": rule_data.get("content")
                })
            
            if "rule_must_test" in rule_id and ("implement" in action_lower or "code" in action_lower):
                applicable_rules.append({
                    "rule": rule_id,
                    "type": "requirement",
                    "content": rule_data.get("content")
                })
            
            if "rule_node_quality" in rule_id and "node" in action_lower:
                applicable_rules.append({
                    "rule": rule_id,
                    "type": "quality",
                    "content": rule_data.get("content")
                })
        
        return {
            "action": action,
            "is_valid": len(violations) == 0,
            "violations": violations,
            "applicable_rules": applicable_rules,
            "recommendation": "Proceed with action" if len(violations) == 0 else "Fix violations before proceeding"
        }
    
    # ===== AGENT ASSISTANCE =====
    
    def get_coding_standards(self) -> Dict[str, Any]:
        """Get all coding standards and guidelines from the graph.
        
        Returns:
            Dictionary with coding standards and best practices.
        """
        standards = {}
        
        if self.kg.graph.has_node("coding_standards"):
            node_data = self.kg.graph.nodes["coding_standards"].get("data", {})
            standards["core"] = node_data.get("content", "")
        
        # Get all rule nodes
        rules = []
        for rule_id in self.kg.find_nodes(type="rule"):
            rule_data = self.kg.graph.nodes[rule_id].get("data", {})
            rules.append({
                "id": rule_id,
                "content": rule_data.get("content", "")
            })
        
        standards["rules"] = rules
        
        # Get instructions
        instructions = []
        for inst_id in self.kg.find_nodes(type="instruction"):
            inst_data = self.kg.graph.nodes[inst_id].get("data", {})
            instructions.append({
                "id": inst_id,
                "content": inst_data.get("content", "")
            })
        
        standards["instructions"] = instructions
        
        return standards
    
    def get_development_context(self, task: str) -> Dict[str, Any]:
        """Get comprehensive development context for a task.
        
        Args:
            task: Description of the development task.
            
        Returns:
            Complete context including standards, current state, and guidance.
        """
        return {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "current_feature": self.get_current_feature_context(),
            "coding_standards": self.get_coding_standards(),
            "graph_stats": self.kg.get_graph_stats(),
            "validation": self.validate_against_rules(task)
        }
    
    def suggest_next_actions(self) -> List[Dict[str, str]]:
        """Suggest next actions based on current state.
        
        Returns:
            List of suggested actions with priorities.
        """
        suggestions = []
        current = self.waterfall.get_current_feature()
        
        if not current:
            suggestions.append({
                "priority": "high",
                "action": "start_feature",
                "description": "Start tracking a new feature with waterfall methodology",
                "command": "python -m ai_dev_graph.cli wf start <id> \"<title>\""
            })
        else:
            # Stage-specific suggestions
            if current.current_stage == WaterfallStage.ANALYSIS:
                suggestions.append({
                    "priority": "high",
                    "action": "complete_analysis",
                    "description": "Define requirements, consult graph for architecture",
                    "command": "Review graph nodes, then: wf advance " + current.feature_id
                })
            
            elif current.current_stage == WaterfallStage.IMPLEMENTATION:
                suggestions.append({
                    "priority": "high",
                    "action": "write_tests",
                    "description": "Implement tests in parallel with code (rule: must_test)",
                    "command": "Write tests, commit with: git commit -m 'test: ...'"
                })
            
            elif current.current_stage == WaterfallStage.TESTING:
                suggestions.append({
                    "priority": "high",
                    "action": "run_tests",
                    "description": "Execute full test suite and validate coverage",
                    "command": "pytest --cov=ai_dev_graph"
                })
            
            elif current.current_stage == WaterfallStage.DOCUMENTATION:
                suggestions.append({
                    "priority": "high",
                    "action": "update_docs",
                    "description": "Update README, add nodes to graph",
                    "command": "Update docs and graph nodes"
                })
        
        # Always suggest validation
        suggestions.append({
            "priority": "medium",
            "action": "validate_graph",
            "description": "Validate graph integrity",
            "command": "python -m ai_dev_graph.cli validate"
        })
        
        return suggestions
    
    # ===== EXPORT FOR AGENTS =====
    
    def export_for_agent(self, agent_type: str = "claude") -> Dict[str, Any]:
        """Export optimized knowledge for AI agents.
        
        Args:
            agent_type: Type of agent (claude, copilot, etc).
            
        Returns:
            Optimized knowledge structure for the agent.
        """
        export_data = {
            "meta": {
                "export_time": datetime.now().isoformat(),
                "agent_type": agent_type,
                "graph_version": "enhanced_mcp_v1"
            },
            "philosophy": {},
            "methodology": {},
            "standards": self.get_coding_standards(),
            "current_context": self.get_current_feature_context(),
            "suggestions": self.suggest_next_actions(),
            "graph_structure": {
                "total_nodes": self.kg.graph.number_of_nodes(),
                "total_edges": self.kg.graph.number_of_edges(),
                "node_types": self.kg.get_graph_stats().get("node_types", {})
            }
        }
        
        # Add philosophy
        if self.kg.graph.has_node("philosophy"):
            phil_data = self.kg.graph.nodes["philosophy"].get("data", {})
            export_data["philosophy"] = {
                "content": phil_data.get("content", ""),
                "principles": "GRAFO · PYTHON · API · DOC · TEST"
            }
        
        # Add waterfall methodology
        if self.kg.graph.has_node("waterfall_methodology"):
            wf_data = self.kg.graph.nodes["waterfall_methodology"].get("data", {})
            export_data["methodology"] = {
                "type": "waterfall",
                "description": wf_data.get("content", ""),
                "stages": self.get_waterfall_stages()
            }
        
        return export_data


# Singleton instance for easy access
_mcp_server_instance = None

def get_mcp_server() -> EnhancedMCPServer:
    """Get or create MCP server singleton instance.
    
    Returns:
        Enhanced MCP server instance.
    """
    global _mcp_server_instance
    if _mcp_server_instance is None:
        from ai_dev_graph.models.manager import get_graph_manager
        manager = get_graph_manager()
        _mcp_server_instance = EnhancedMCPServer(manager)
    return _mcp_server_instance
