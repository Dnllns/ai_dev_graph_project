"""Comprehensive tests for AI Dev Graph functionality."""

import pytest
import tempfile
import os
from pathlib import Path

from ai_dev_graph.domain.graph import KnowledgeGraph
from ai_dev_graph.domain.models import NodeData, NodeType
from ai_dev_graph.application.manager import GraphManager
from ai_dev_graph.infrastructure.networkx_repo import NetworkXSQLiteRepository
from ai_dev_graph.init_meta_graph import init_project_graph


@pytest.fixture
def kg():
    """Fixture for a clean knowledge graph."""
    # Using a temporary db for testing
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    repo = NetworkXSQLiteRepository(db_path=db_path)
    kg = KnowledgeGraph(repository=repo)
    yield kg
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

class TestKnowledgeGraph:
    """Tests for core graph functionality."""

    def test_graph_node_addition(self, kg):
        """Validate node and edge addition."""
        root = NodeData(id="root", type=NodeType.PROJECT, content="root node")
        child = NodeData(id="child", type=NodeType.CONCEPT, content="child node")
        
        kg.add_knowledge(root)
        kg.add_knowledge(child, parents=["root"])
        
        assert kg.has_node("root")
        assert kg.has_node("child")
        assert "child" in kg.get_successors("root")
        assert kg.get_node_data("root").content == "root node"
    
    def test_node_context_retrieval(self, kg):
        """Test context retrieval for nodes."""
        root = NodeData(id="root", type=NodeType.PROJECT, content="root")
        child1 = NodeData(id="child1", type=NodeType.CONCEPT, content="child 1")
        child2 = NodeData(id="child2", type=NodeType.CONCEPT, content="child 2")
        
        kg.add_knowledge(root)
        kg.add_knowledge(child1, parents=["root"])
        kg.add_knowledge(child2, parents=["root"])
        
        context = kg.get_context("root")
        
        assert context["parents"] == []
        assert set(context["children"]) == {"child1", "child2"}
    
    def test_find_nodes_by_type(self, kg):
        """Test finding nodes by type."""
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
    
    def test_find_nodes_by_content(self, kg):
        """Test finding nodes by content match."""
        kg.add_knowledge(NodeData(id="n1", type=NodeType.CONCEPT, content="This is about testing"))
        kg.add_knowledge(NodeData(id="n2", type=NodeType.CONCEPT, content="Another concept"))
        kg.add_knowledge(NodeData(id="n3", type=NodeType.CONCEPT, content="Testing again"))
        
        results = kg.find_nodes(content_match="testing")
        assert set(results) == {"n1", "n3"}
    
    def test_node_update(self, kg):
        """Test updating node content and metadata."""
        node = NodeData(id="test", type=NodeType.CONCEPT, content="original")
        kg.add_knowledge(node)
        
        success = kg.update_node("test", content="updated", metadata={"key": "value"})
        assert success
        
        updated = kg.get_node_data("test")
        assert updated.content == "updated"
        assert updated.metadata["key"] == "value"
    
    def test_node_deletion(self, kg):
        """Test deleting nodes."""
        kg.add_knowledge(NodeData(id="test", type=NodeType.CONCEPT, content="test"))
        assert kg.has_node("test")
        
        success = kg.delete_node("test")
        assert success
        assert not kg.has_node("test")
    
    def test_graph_statistics(self, kg):
        """Test statistics calculation."""
        kg.add_knowledge(NodeData(id="p1", type=NodeType.PROJECT, content="p"))
        kg.add_knowledge(NodeData(id="c1", type=NodeType.CONCEPT, content="c"))
        kg.add_knowledge(NodeData(id="r1", type=NodeType.RULE, content="r"), parents=["p1"])
        
        stats = kg.get_graph_stats()
        
        assert stats["total_nodes"] == 3
        assert stats["total_edges"] == 1
        assert "node_types" in stats
        assert "project" in stats["node_types"]


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
            # We need to mock DB path for manager to avoid conflict with real data
            # Simplified for test
            manager = GraphManager(tmpdir)
            kg = manager.load_or_create()
            assert kg is not None
            assert manager.current_graph is not None


class TestInitMetaGraph:
    """Tests for meta graph initialization."""
    
    def test_project_graph_initialization(self):
        """Test that project graph initializes with core nodes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to tmpdir to avoid overriding local graph
            os.chdir(tmpdir)
            os.makedirs("graphs", exist_ok=True)
            
            kg = init_project_graph()
            
            assert kg.has_node("ai_dev_graph")
            assert kg.has_node("philosophy")
            assert kg.has_node("coding_standards")


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_full_workflow(self, kg):
        """Test complete workflow: create, query, update, delete."""
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
        
        # Stats
        stats = kg.get_graph_stats()
        assert stats["total_nodes"] == 2