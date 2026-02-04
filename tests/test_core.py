"""Comprehensive tests for AI Dev Graph functionality."""

import pytest
import json
import tempfile
import os
from pathlib import Path

from ai_dev_graph.core.graph import KnowledgeGraph, NodeData, NodeType
from ai_dev_graph.init_meta_graph import init_project_graph
from ai_dev_graph.models.manager import GraphManager


class TestKnowledgeGraph:
    """Tests for core graph functionality."""
    
    def test_graph_node_addition(self):
        """Validate node and edge addition."""
        kg = KnowledgeGraph()
        
        root = NodeData(id="root", type=NodeType.PROJECT, content="root node")
        child = NodeData(id="child", type=NodeType.CONCEPT, content="child node")
        
        kg.add_knowledge(root)
        kg.add_knowledge(child, parents=["root"])
        
        assert kg.graph.has_node("root")
        assert kg.graph.has_node("child")
        assert kg.graph.has_edge("root", "child")
        assert kg.graph.nodes["root"]["data"]["content"] == "root node"
    
    def test_node_context_retrieval(self):
        """Test context retrieval for nodes."""
        kg = KnowledgeGraph()
        
        root = NodeData(id="root", type=NodeType.PROJECT, content="root")
        child1 = NodeData(id="child1", type=NodeType.CONCEPT, content="child 1")
        child2 = NodeData(id="child2", type=NodeType.CONCEPT, content="child 2")
        
        kg.add_knowledge(root)
        kg.add_knowledge(child1, parents=["root"])
        kg.add_knowledge(child2, parents=["root"])
        
        context = kg.get_context("root")
        
        assert context["parents"] == []
        assert set(context["children"]) == {"child1", "child2"}
    
    def test_find_nodes_by_type(self):
        """Test finding nodes by type."""
        kg = KnowledgeGraph()
        
        nodes = [
            NodeData(id="p1", type=NodeType.PROJECT, content="project 1"),
            NodeData(id="c1", type=NodeType.CONCEPT, content="concept 1"),
            NodeData(id="r1", type=NodeType.RULE, content="rule 1"),
        ]
        
        for node in nodes:
            kg.add_knowledge(node)
        
        concepts = kg.find_nodes(type=NodeType.CONCEPT)
        assert concepts == ["c1"]
        
        rules = kg.find_nodes(type=NodeType.RULE)
        assert rules == ["r1"]
    
    def test_find_nodes_by_content(self):
        """Test finding nodes by content match."""
        kg = KnowledgeGraph()
        
        kg.add_knowledge(NodeData(id="n1", type=NodeType.CONCEPT, content="This is about testing"))
        kg.add_knowledge(NodeData(id="n2", type=NodeType.CONCEPT, content="Another concept"))
        kg.add_knowledge(NodeData(id="n3", type=NodeType.CONCEPT, content="Testing again"))
        
        results = kg.find_nodes(content_match="testing")
        assert set(results) == {"n1", "n3"}
    
    def test_node_update(self):
        """Test updating node content and metadata."""
        kg = KnowledgeGraph()
        
        node = NodeData(id="test", type=NodeType.CONCEPT, content="original")
        kg.add_knowledge(node)
        
        success = kg.update_node("test", content="updated", metadata={"key": "value"})
        assert success
        
        updated = kg.graph.nodes["test"]["data"]
        assert updated["content"] == "updated"
        assert updated["metadata"]["key"] == "value"
    
    def test_node_deletion(self):
        """Test deleting nodes."""
        kg = KnowledgeGraph()
        
        kg.add_knowledge(NodeData(id="test", type=NodeType.CONCEPT, content="test"))
        assert kg.graph.has_node("test")
        
        success = kg.delete_node("test")
        assert success
        assert not kg.graph.has_node("test")
    
    def test_graph_persistence(self):
        """Test save and load functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_graph.json")
            
            # Create and save
            kg1 = KnowledgeGraph()
            kg1.add_knowledge(NodeData(id="n1", type=NodeType.PROJECT, content="project"))
            kg1.add_knowledge(NodeData(id="n2", type=NodeType.CONCEPT, content="concept"), parents=["n1"])
            kg1.save(filepath)
            
            # Load and verify
            kg2 = KnowledgeGraph()
            kg2.load(filepath)
            
            assert kg2.graph.has_node("n1")
            assert kg2.graph.has_node("n2")
            assert kg2.graph.has_edge("n1", "n2")
    
    def test_graph_statistics(self):
        """Test statistics calculation."""
        kg = KnowledgeGraph()
        
        kg.add_knowledge(NodeData(id="p1", type=NodeType.PROJECT, content="p"))
        kg.add_knowledge(NodeData(id="c1", type=NodeType.CONCEPT, content="c"))
        kg.add_knowledge(NodeData(id="r1", type=NodeType.RULE, content="r"), parents=["p1"])
        
        stats = kg.get_graph_stats()
        
        assert stats["total_nodes"] == 3
        assert stats["total_edges"] == 1
        assert "node_types" in stats
        assert NodeType.PROJECT in stats["node_types"]


class TestGraphManager:
    """Tests for high-level graph management."""
    
    def test_manager_initialization(self):
        """Test GraphManager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = GraphManager(tmpdir)
            assert manager.storage_dir == Path(tmpdir)
    
    def test_load_or_create(self):
        """Test loading or creating graphs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = GraphManager(tmpdir)
            
            # Create new
            kg = manager.load_or_create()
            assert kg is not None
            assert manager.current_graph is not None
    
    def test_save_with_backup(self):
        """Test saving with automatic backups."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = GraphManager(tmpdir)
            kg = manager.load_or_create()
            
            # First save
            success = manager.save_with_backup()
            assert success
            assert (Path(tmpdir) / "v0_initial.json").exists()
            
            # Update and save again
            kg.add_knowledge(NodeData(id="new", type=NodeType.CONCEPT, content="new"))
            success = manager.save_with_backup()
            assert success
            
            # Check backup was created
            backup_files = list(Path(tmpdir).glob("v0_initial_backup_*.json"))
            assert len(backup_files) > 0
    
    def test_graph_validation(self):
        """Test graph validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = GraphManager(tmpdir)
            kg = manager.load_or_create()
            
            report = manager.validate_graph()
            
            assert "valid" in report
            assert "total_nodes" in report
            assert "total_edges" in report
    
    def test_export_for_agent(self):
        """Test exporting graph for agent consumption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = GraphManager(tmpdir)
            kg = manager.load_or_create()
            
            kg.add_knowledge(NodeData(id="n1", type=NodeType.CONCEPT, content="concept"))
            
            export = manager.export_for_agent("claude")
            
            assert "export_date" in export
            assert "agent_type" in export
            assert export["agent_type"] == "claude"
            assert "statistics" in export
            assert "nodes_by_type" in export
    
    def test_statistics_and_recommendations(self):
        """Test statistics and recommendations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = GraphManager(tmpdir)
            kg = manager.load_or_create()
            
            stats = manager.get_statistics()
            
            assert "total_nodes" in stats
            assert "recommendations" in stats
            
            # Empty graph should have recommendations
            recommendations = manager.get_recommendations()
            assert isinstance(recommendations, list)


class TestInitMetaGraph:
    """Tests for meta graph initialization."""
    
    def test_project_graph_initialization(self):
        """Test that project graph initializes with core nodes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            os.makedirs("graphs", exist_ok=True)
            
            kg = init_project_graph()
            
            assert kg.graph.has_node("ai_dev_graph")
            assert kg.graph.has_node("philosophy")
            assert kg.graph.has_node("coding_standards")
            assert kg.graph.has_node("version_control")


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_full_workflow(self):
        """Test complete workflow: create, query, update, delete."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a clean graph manager without initializing project graph
            manager = GraphManager(tmpdir)
            kg = KnowledgeGraph()  # Fresh empty graph
            manager.current_graph = kg
            
            # Create nodes
            root = NodeData(id="project", type=NodeType.PROJECT, content="Main project")
            feature = NodeData(id="feature_x", type=NodeType.CONCEPT, content="Feature X")
            
            kg.add_knowledge(root)
            kg.add_knowledge(feature, parents=["project"])
            
            # Query
            context = kg.get_context("project")
            assert "feature_x" in context["children"]
            
            # Update
            success = kg.update_node("feature_x", content="Feature X - Updated")
            assert success
            
            # Save and validate
            manager.save_with_backup()
            
            validation = manager.validate_graph()
            assert validation["total_nodes"] == 2


# Run all tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])