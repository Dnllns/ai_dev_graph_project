"""Tests for Advanced MCP Server functionality."""

import pytest
from ai_dev_graph.advanced_mcp import AdvancedMCPServer
from ai_dev_graph.application.manager import GraphManager
from ai_dev_graph.domain.models import NodeData, NodeType


@pytest.fixture
def mcp_server(force_test_db):
    """Create an MCP server instance for testing."""
    manager = GraphManager()
    server = AdvancedMCPServer(manager)

    # Add test nodes using add_knowledge
    server.kg.add_knowledge(
        NodeData(
            id="test_concept_1",
            type=NodeType.CONCEPT,
            content="Clean Architecture principles for software design",
            metadata={"category": "architecture"},
        )
    )

    server.kg.add_knowledge(
        NodeData(
            id="test_concept_2",
            type=NodeType.CONCEPT,
            content="SOLID principles: Single Responsibility, Open-Closed, Liskov Substitution",
            metadata={"category": "principles"},
        )
    )

    server.kg.add_knowledge(
        NodeData(
            id="test_guideline_1",
            type=NodeType.GUIDELINE,
            content="Dependency Inversion Principle",
            metadata={"category": "solid"},
        )
    )

    # Add edges using the repository directly
    server.kg.repo.add_edge("test_concept_1", "test_concept_2")
    server.kg.repo.add_edge("test_concept_2", "test_guideline_1")

    return server


class TestGraphTraversal:
    """Test graph traversal capabilities."""

    def test_traverse_graph_forward(self, mcp_server):
        """Test forward traversal from a node."""
        result = mcp_server.traverse_graph(
            "test_concept_1", max_depth=2, direction="forward"
        )

        assert result["start_node"] == "test_concept_1"
        assert result["nodes_visited"] >= 2
        assert 0 in result["nodes_by_depth"]
        assert len(result["nodes_by_depth"][0]) == 1

    def test_traverse_graph_with_filter(self, mcp_server):
        """Test traversal with node type filter."""
        result = mcp_server.traverse_graph(
            "test_concept_1",
            max_depth=2,
            direction="forward",
            node_filter={"type": "guideline"},
        )

        # Should find the principle node
        nodes_found = []
        for depth_nodes in result["nodes_by_depth"].values():
            nodes_found.extend([n["id"] for n in depth_nodes])

        assert "test_guideline_1" in nodes_found

    def test_find_shortest_path(self, mcp_server):
        """Test shortest path finding."""
        path = mcp_server.find_shortest_path("test_concept_1", "test_guideline_1")

        assert path is not None
        assert path[0] == "test_concept_1"
        assert path[-1] == "test_guideline_1"
        assert len(path) == 3  # concept_1 -> concept_2 -> principle_1

    def test_find_shortest_path_no_connection(self, mcp_server):
        """Test shortest path when no connection exists."""
        # Add isolated node
        mcp_server.kg.add_knowledge(
            NodeData(
                id="isolated_node",
                type=NodeType.CONCEPT,
                content="Isolated concept",
                metadata={},
            )
        )

        path = mcp_server.find_shortest_path("test_concept_1", "isolated_node")
        assert path is None

    def test_get_node_neighborhood(self, mcp_server):
        """Test getting node neighborhood."""
        neighborhood = mcp_server.get_node_neighborhood("test_concept_2", radius=1)

        assert neighborhood["center"] == "test_concept_2"
        assert "test_concept_2" in neighborhood["nodes"]
        assert len(neighborhood["edges"]) > 0


class TestSemanticSearch:
    """Test semantic search capabilities."""

    def test_semantic_search_basic(self, mcp_server):
        """Test basic semantic search."""
        results = mcp_server.semantic_search("architecture", limit=5)

        assert len(results) > 0
        assert any("architecture" in r["content"].lower() for r in results)
        assert all("score" in r for r in results)

    def test_semantic_search_with_type_filter(self, mcp_server):
        """Test semantic search with type filtering."""
        results = mcp_server.semantic_search(
            "principles", node_types=["concept"], limit=5
        )

        assert all(r["type"] == "concept" for r in results)

    def test_semantic_search_scoring(self, mcp_server):
        """Test that results are properly scored and sorted."""
        results = mcp_server.semantic_search("SOLID", limit=5)

        # Results should be sorted by score
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_find_related_nodes(self, mcp_server):
        """Test finding related nodes."""
        related = mcp_server.find_related_nodes("test_concept_1", max_results=5)

        # Should find nodes through graph structure
        assert isinstance(related, list)


class TestLinkPrediction:
    """Test link prediction capabilities."""

    def test_predict_missing_links(self, mcp_server):
        """Test missing link prediction."""
        # Add more nodes to make predictions meaningful
        mcp_server.kg.add_knowledge(
            NodeData(
                id="test_concept_3",
                type=NodeType.CONCEPT,
                content="Design patterns and architecture",
                metadata={},
            )
        )

        predictions = mcp_server.predict_missing_links(
            min_score=0.1, max_predictions=10
        )

        assert isinstance(predictions, list)
        for pred in predictions:
            assert "source" in pred
            assert "target" in pred
            assert "score" in pred
            assert "reason" in pred
            assert 0 <= pred["score"] <= 1

    def test_suggest_new_links(self, mcp_server):
        """Test suggesting new links for a specific node."""
        suggestions = mcp_server.suggest_new_links("test_concept_1", max_suggestions=3)

        assert isinstance(suggestions, list)
        for sugg in suggestions:
            assert "target" in sugg
            assert "score" in sugg
            assert "reason" in sugg


class TestGraphAnalysis:
    """Test graph analysis capabilities."""

    def test_analyze_node_importance(self, mcp_server):
        """Test node importance analysis."""
        importance = mcp_server.analyze_node_importance()

        assert len(importance) > 0
        assert all("importance_score" in node for node in importance)
        assert all("in_degree" in node for node in importance)
        assert all("out_degree" in node for node in importance)

        # Scores should be sorted
        scores = [n["importance_score"] for n in importance]
        assert scores == sorted(scores, reverse=True)

    def test_detect_communities(self, mcp_server):
        """Test community detection."""
        communities = mcp_server.detect_communities()

        assert isinstance(communities, dict)
        # All test nodes should be in the same community (they're connected)
        all_nodes = []
        for community in communities.values():
            all_nodes.extend(community)

        assert "test_concept_1" in all_nodes
        assert "test_concept_2" in all_nodes

    def test_get_graph_metrics(self, mcp_server):
        """Test comprehensive graph metrics."""
        metrics = mcp_server.get_graph_metrics()

        assert "total_nodes" in metrics
        assert "total_edges" in metrics
        assert "node_types" in metrics
        assert "average_degree" in metrics
        assert "density" in metrics

        assert metrics["total_nodes"] >= 3
        assert metrics["total_edges"] >= 2


class TestLegacyCompatibility:
    """Test backward compatibility with original MCP server."""

    def test_get_node(self, mcp_server):
        """Test legacy get_node method."""
        result = mcp_server.get_node("test_concept_1")

        assert "node" in result
        assert result["node"]["id"] == "test_concept_1"

    def test_search_nodes(self, mcp_server):
        """Test legacy search_nodes method."""
        results = mcp_server.search_nodes("architecture", limit=5)

        assert len(results) > 0
        assert all("id" in r for r in results)

    def test_export_for_agent(self, mcp_server):
        """Test agent export functionality."""
        export = mcp_server.export_for_agent("claude")

        assert "meta" in export
        assert "graph_metrics" in export
        assert "important_nodes" in export
        assert export["meta"]["graph_version"] == "advanced_v2"
