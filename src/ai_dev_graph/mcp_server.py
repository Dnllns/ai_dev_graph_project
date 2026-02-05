"""Enhanced MCP Server for AI Dev Graph - Model Context Protocol Interface."""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from ai_dev_graph.domain.models import NodeType
from ai_dev_graph.application.manager import GraphManager, get_graph_manager
from ai_dev_graph.waterfall_tracker import WaterfallTracker, WaterfallStage

logger = logging.getLogger(__name__)


class EnhancedMCPServer:
    """Enhanced MCP Server following Clean Architecture principles."""
    
    def __init__(self, graph_manager: GraphManager):
        self.graph_manager = graph_manager
        self.kg = graph_manager.load_or_create()
        self.waterfall = WaterfallTracker()
    
    # ===== CORE GRAPH OPERATIONS =====
    
    def get_node(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        return self.kg.get_context(node_id, depth=depth)
    
    def search_nodes(self, query: str, node_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        filters = {"content_match": query}
        if node_type:
            filters["type"] = node_type
        
        node_ids = self.kg.find_nodes(**filters)
        results = []
        
        for node_id in node_ids[:limit]:
            node = self.kg.get_node_data(node_id)
            if not node:
                continue
                
            content = node.content
            # Simple relevance scoring
            relevance = content.lower().count(query.lower())
            
            results.append({
                "id": node_id,
                "type": node.type.value,
                "content": content,
                "relevance": relevance,
                "parents": self.kg.get_predecessors(node_id),
                "children": self.kg.get_successors(node_id)
            })
        
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results
    
    # ===== WATERFALL METHODOLOGY =====
    
    def get_waterfall_stages(self) -> List[Dict[str, str]]:
        stages = []
        stage_nodes = [
            "stage_analysis", "stage_design", "stage_implementation",
            "stage_testing", "stage_documentation", "stage_release"
        ]
        
        for stage_id in stage_nodes:
            node = self.kg.get_node_data(stage_id)
            if node:
                stages.append({
                    "id": stage_id,
                    "name": stage_id.replace("stage_", "").upper(),
                    "description": node.content
                })
        
        return stages
    
    def get_current_feature_context(self) -> Dict[str, Any]:
        current = self.waterfall.get_current_feature()
        
        if not current:
            return {
                "status": "no_active_feature",
                "message": "No feature currently being tracked",
                "recommendation": "Start a new feature with: waterfall start <id> <title>"
            }
        
        stage_node_id = f"stage_{current.current_stage.value}"
        stage_guidance = {}
        
        node = self.kg.get_node_data(stage_node_id)
        if node:
            stage_guidance = {
                "stage": current.current_stage.value,
                "guidance": node.content,
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
        rule_nodes = self.kg.find_nodes(type="rule")
        applicable_rules = []
        violations = []
        
        for rule_id in rule_nodes:
            node = self.kg.get_node_data(rule_id)
            if not node:
                continue
                
            rule_content = node.content.lower()
            action_lower = action.lower()
            
            if "rule_no_skip_stages" in rule_id and "skip" in action_lower:
                violations.append({
                    "rule": rule_id,
                    "severity": "error",
                    "message": node.content
                })
            
            if "rule_must_test" in rule_id and ("implement" in action_lower or "code" in action_lower):
                applicable_rules.append({
                    "rule": rule_id,
                    "type": "requirement",
                    "content": node.content
                })
        
        return {
            "action": action,
            "is_valid": len(violations) == 0,
            "violations": violations,
            "applicable_rules": applicable_rules,
            "recommendation": "Proceed" if len(violations) == 0 else "Fix violations"
        }
    
    # ===== AGENT ASSISTANCE =====
    
    def get_coding_standards(self) -> Dict[str, Any]:
        standards = {}
        
        node = self.kg.get_node_data("coding_standards")
        if node:
            standards["core"] = node.content
        
        rules = []
        for rule_id in self.kg.find_nodes(type="rule"):
            node = self.kg.get_node_data(rule_id)
            if node:
                rules.append({"id": rule_id, "content": node.content})
        standards["rules"] = rules
        
        instructions = []
        for inst_id in self.kg.find_nodes(type="instruction"):
            node = self.kg.get_node_data(inst_id)
            if node:
                instructions.append({"id": inst_id, "content": node.content})
        standards["instructions"] = instructions
        
        return standards
    
    def get_development_context(self, task: str) -> Dict[str, Any]:
        return {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "current_feature": self.get_current_feature_context(),
            "coding_standards": self.get_coding_standards(),
            "graph_stats": self.kg.get_graph_stats(),
            "validation": self.validate_against_rules(task)
        }
    
    def suggest_next_actions(self) -> List[Dict[str, str]]:
        suggestions = []
        current = self.waterfall.get_current_feature()
        
        if not current:
            suggestions.append({
                "priority": "high",
                "action": "start_feature",
                "description": "Start tracking a new feature",
                "command": "python -m ai_dev_graph.cli wf start <id> \"<title>\""
            })
        else:
            if current.current_stage == WaterfallStage.ANALYSIS:
                suggestions.append({"priority": "high", "action": "complete_analysis", "description": "Define requirements", "command": "wf advance " + current.feature_id})
            elif current.current_stage == WaterfallStage.IMPLEMENTATION:
                suggestions.append({"priority": "high", "action": "write_tests", "description": "Implement tests", "command": "git commit -m 'test: ...'"})
        
        suggestions.append({"priority": "medium", "action": "validate_graph", "description": "Validate graph integrity", "command": "python -m ai_dev_graph.cli validate"})
        return suggestions
    
    def export_for_agent(self, agent_type: str = "claude") -> Dict[str, Any]:
        export_data = {
            "meta": {"export_time": datetime.now().isoformat(), "agent_type": agent_type, "graph_version": "clean_arch_v1"},
            "philosophy": {},
            "methodology": {},
            "standards": self.get_coding_standards(),
            "current_context": self.get_current_feature_context(),
            "suggestions": self.suggest_next_actions(),
            "graph_structure": self.kg.get_graph_stats()
        }
        
        phil = self.kg.get_node_data("philosophy")
        if phil:
            export_data["philosophy"] = {"content": phil.content, "principles": "GRAFO · PYTHON · API · DOC · TEST"}
            
        wf = self.kg.get_node_data("waterfall_methodology")
        if wf:
            export_data["methodology"] = {"type": "waterfall", "description": wf.content, "stages": self.get_waterfall_stages()}
            
        return export_data


_mcp_server_instance = None

def get_mcp_server() -> EnhancedMCPServer:
    global _mcp_server_instance
    if _mcp_server_instance is None:
        manager = get_graph_manager()
        _mcp_server_instance = EnhancedMCPServer(manager)
    return _mcp_server_instance
