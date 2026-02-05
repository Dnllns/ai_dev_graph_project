import pytest
from unittest.mock import MagicMock, patch, ANY
import json
from ai_dev_graph.core.config import DatabaseType
from ai_dev_graph.infrastructure.persistence_factory import PersistenceFactory
from ai_dev_graph.infrastructure.neo4j_repo import Neo4jRepository
from ai_dev_graph.infrastructure.networkx_repo import NetworkXSQLiteRepository
from ai_dev_graph.domain.models import NodeData, NodeType

class TestPersistenceFactory:
    def teardown_method(self):
        PersistenceFactory.reset()

    def test_factory_returns_sqlite_by_default_mocked(self):
        """Test that factory returns SQLite repo when configured."""
        with patch("ai_dev_graph.infrastructure.persistence_factory.settings") as mock_settings:
            mock_settings.database_type = DatabaseType.SQLITE
            mock_settings.sqlite_path = ":memory:"
            
            repo = PersistenceFactory.get_repository()
            assert isinstance(repo, NetworkXSQLiteRepository)

    def test_factory_returns_neo4j_when_configured(self):
        """Test that factory attempts to create Neo4j repo when configured."""
        with patch("ai_dev_graph.infrastructure.persistence_factory.settings") as mock_settings, \
             patch("ai_dev_graph.infrastructure.neo4j_repo.Neo4jDriver") as mock_class:
            
            mock_settings.database_type = DatabaseType.NEO4J
            mock_settings.neo4j_uri = "bolt://localhost:7687"
            
            # Setup mock driver to succeed
            driver_instance = MagicMock()
            mock_class.driver.return_value = driver_instance
            
            repo = PersistenceFactory.get_repository()
            assert isinstance(repo, Neo4jRepository)
            mock_class.driver.assert_called_once()
            driver_instance.verify_connectivity.assert_called_once()

    def test_factory_handles_neo4j_connection_error(self):
        """Test proper error propagation on connection failure."""
        with patch("ai_dev_graph.infrastructure.persistence_factory.settings") as mock_settings, \
             patch("ai_dev_graph.infrastructure.neo4j_repo.Neo4jDriver") as mock_class:
            
            mock_settings.database_type = DatabaseType.NEO4J
            mock_class.driver.side_effect = Exception("Connection refused")
            
            with pytest.raises(Exception):
                PersistenceFactory.get_repository()


class TestNeo4jRepository:
    @pytest.fixture
    def mock_driver_instance(self):
        """Yields the MOCK INSTANCE of the driver."""
        with patch("ai_dev_graph.infrastructure.neo4j_repo.Neo4jDriver") as mock_class:
            driver_instance = MagicMock()
            mock_class.driver.return_value = driver_instance
            yield driver_instance

    @pytest.fixture
    def repo(self, mock_driver_instance):
        return Neo4jRepository(uri="bolt://test", user="u", password="p", database="neo4j")

    def test_init_verifies_connectivity(self, mock_driver_instance):
        # When initializing repository (which happens in the test body here)
        Neo4jRepository(uri="bolt://test")
        
        # We verify that verify_connectivity was called on the instance
        mock_driver_instance.verify_connectivity.assert_called_once()

    def test_add_node_generates_correct_cypher(self, repo, mock_driver_instance):
        # Setup session mock
        session_mock = MagicMock()
        # mock_driver_instance is the 'self.driver'. 
        # self.driver.session(...) returns a "session context provider"
        # .__enter__() returns the actual session
        mock_driver_instance.session.return_value.__enter__.return_value = session_mock
        
        node = NodeData(
            id="test_node", 
            type=NodeType.CONCEPT, 
            content="test content",
            metadata={"priority": "high"}
        )
        
        repo.add_node(node)
        
        # Verify the query
        session_mock.run.assert_called_once()
        args, kwargs = session_mock.run.call_args
        query = args[0]
        
        assert "MERGE (n:Node {id: $id})" in query
        assert "n:Concept" in query  # Capitalized type
        assert "n.content = $content" in query
        assert kwargs["id"] == "test_node"
        assert kwargs["content"] == "test content"
        assert "priority" in kwargs["metadata"]

    def test_add_edge_generates_correct_cypher(self, repo, mock_driver_instance):
        session_mock = MagicMock()
        mock_driver_instance.session.return_value.__enter__.return_value = session_mock
        
        repo.add_edge("source", "target")
        
        session_mock.run.assert_called_once()
        args, kwargs = session_mock.run.call_args
        query = args[0]
        
        assert "MATCH (a:Node {id: $source_id})" in query
        assert "MERGE (a)-[r:RELATED_TO]->(b)" in query
        assert kwargs["source_id"] == "source"
        assert kwargs["target_id"] == "target"

    def test_get_node_maps_result_correctly(self, repo, mock_driver_instance):
        session_mock = MagicMock()
        mock_driver_instance.session.return_value.__enter__.return_value = session_mock
        
        # Mock result record
        # Note: In _map_to_nodedata, we do dict(neo4j_node). 
        # So we need mock_record['n'] to be something that behaves like a dict or can be converted.
        mock_node_payload = {
            "id": "found_node",
            "type": "concept",
            "content": "found content",
            "metadata": '{"key": "val"}'
        }
        mock_record = {
            "n": mock_node_payload
        }
        
        mock_result = MagicMock()
        mock_result.single.return_value = mock_record
        session_mock.run.return_value = mock_result
        
        node = repo.get_node("found_node")
        
        assert node is not None
        assert node.id == "found_node"
        assert node.type == NodeType.CONCEPT
        assert node.metadata == {"key": "val"}

    def test_find_nodes_filtering(self, repo, mock_driver_instance):
        session_mock = MagicMock()
        mock_driver_instance.session.return_value.__enter__.return_value = session_mock
        
        # Results are records
        mock_result = MagicMock()
        mock_result.__iter__.return_value = [{"n.id": "n1"}, {"n.id": "n2"}]
        session_mock.run.return_value = mock_result
        
        ids = repo.find_nodes(type=NodeType.RULE, content_match="urgent")
        
        session_mock.run.assert_called_once()
        args, kwargs = session_mock.run.call_args
        query = args[0]
        
        assert "n.type = $type" in query
        assert "toLower(n.content) CONTAINS" in query
        assert kwargs["type"] == NodeType.RULE
        assert kwargs["content_match"] == "urgent"
        assert len(ids) == 2
