import json
from typing import List, Dict, Any, Optional, Tuple
from neo4j import GraphDatabase as Neo4jDriver
from ai_dev_graph.domain.models import NodeData, NodeType
from ai_dev_graph.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jRepository:
    """Infrastructure implementation using Neo4j for graph persistence."""

    def __init__(
        self,
        uri: str = None,
        user: str = None,
        password: str = None,
        database: str = None,
    ):
        uri = uri or settings.neo4j_uri
        user = user or settings.neo4j_user
        password = password or settings.neo4j_password
        self.database = database or settings.neo4j_db

        try:
            self.driver = Neo4jDriver.driver(uri, auth=(user, password))
            self._verify_connectivity()
            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise e

    def _verify_connectivity(self):
        self.driver.verify_connectivity()

    def close(self):
        if self.driver:
            self.driver.close()

    def add_node(self, node: NodeData) -> None:
        """Add a node to the graph with semantic labels."""
        query = (
            f"MERGE (n:Node {{id: $id}}) "
            f"SET n:{node.type.value.capitalize()}, "
            "n.content = $content, "
            "n.type = $type_val, "
            "n.metadata = $metadata, "
            "n.updated_at = datetime()"
        )
        # We add 'Node' label as base, and specific label based on type

        with self.driver.session(database=self.database) as session:
            session.run(
                query,
                id=node.id,
                content=node.content,
                type_val=node.type.value,
                metadata=json.dumps(node.metadata),
            )

    def add_edge(self, source_id: str, target_id: str) -> None:
        """Add a relationship between two nodes."""
        query = (
            "MATCH (a:Node {id: $source_id}) "
            "MATCH (b:Node {id: $target_id}) "
            "MERGE (a)-[r:RELATED_TO]->(b) "
            "SET r.created_at = datetime()"
        )
        with self.driver.session(database=self.database) as session:
            session.run(query, source_id=source_id, target_id=target_id)

    def get_node(self, node_id: str) -> Optional[NodeData]:
        query = "MATCH (n:Node {id: $id}) RETURN n"
        with self.driver.session(database=self.database) as session:
            result = session.run(query, id=node_id)
            record = result.single()
            if record:
                node = record["n"]
                return self._map_to_nodedata(node)
            return None

    def get_all_nodes(self) -> List[NodeData]:
        query = "MATCH (n:Node) RETURN n"
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            return [self._map_to_nodedata(record["n"]) for record in result]

    def get_all_edges(self) -> List[Tuple[str, str]]:
        query = "MATCH (a:Node)-[:RELATED_TO]->(b:Node) RETURN a.id, b.id"
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            return [(record["a.id"], record["b.id"]) for record in result]

    def update_node(
        self,
        node_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        sets = ["n.updated_at = datetime()"]
        params = {"id": node_id}

        if content is not None:
            sets.append("n.content = $content")
            params["content"] = content

        if metadata is not None:
            # For partial update, we first might need to read?
            # Or just overwrite if that's the contract.
            # Protocol doc says: "Update node content or metadata."
            # The sqlite version does a merge.
            sets.append(
                "n.metadata = $metadata"
            )  # We overwrite the metadata blob for now to be safe/simple
            params["metadata"] = json.dumps(metadata)

        set_clause = ", ".join(sets)
        query = f"MATCH (n:Node {{id: $id}}) SET {set_clause} RETURN count(n) as c"

        with self.driver.session(database=self.database) as session:
            result = session.run(query, **params)
            count = result.single()["c"]
            return count > 0

    def delete_node(self, node_id: str) -> bool:
        query = "MATCH (n:Node {id: $id}) DETACH DELETE n RETURN count(n) as c"
        with self.driver.session(database=self.database) as session:
            result = session.run(query, id=node_id)
            count = result.single()["c"]
            return count > 0

    def find_nodes(self, **filters) -> List[str]:
        # Dynamic query building
        clauses = ["MATCH (n:Node)"]
        where_conditions = []
        params = {}

        if "type" in filters:
            where_conditions.append("n.type = $type")
            params["type"] = filters["type"]

        if "content_match" in filters:
            # Case insensitive search
            where_conditions.append(
                "toLower(n.content) CONTAINS toLower($content_match)"
            )
            params["content_match"] = filters["content_match"]

        if where_conditions:
            clauses.append("WHERE " + " AND ".join(where_conditions))

        clauses.append("RETURN n.id")
        query = " ".join(clauses)

        with self.driver.session(database=self.database) as session:
            result = session.run(query, **params)
            return [record["n.id"] for record in result]

    def get_neighbors(self, node_id: str) -> Dict[str, List[str]]:
        query_parents = "MATCH (p:Node)-[:RELATED_TO]->(n:Node {id: $id}) RETURN p.id"
        query_children = "MATCH (n:Node {id: $id})-[:RELATED_TO]->(c:Node) RETURN c.id"

        with self.driver.session(database=self.database) as session:
            parents = [r["p.id"] for r in session.run(query_parents, id=node_id)]
            children = [r["c.id"] for r in session.run(query_children, id=node_id)]

        return {"parents": parents, "children": children}

    def get_stats(self) -> Dict[str, Any]:
        with self.driver.session(database=self.database) as session:
            nodes = session.run("MATCH (n:Node) RETURN count(n) as c").single()["c"]
            edges = session.run(
                "MATCH ()-[r:RELATED_TO]->() RETURN count(r) as c"
            ).single()["c"]

            # Distribution
            dist = session.run("MATCH (n:Node) RETURN n.type as type, count(n) as c")
            node_types = {r["type"]: r["c"] for r in dist}

            return {
                "total_nodes": nodes,
                "total_edges": edges,
                "node_types": node_types,
            }

    def _map_to_nodedata(self, neo4j_node) -> NodeData:
        data = dict(neo4j_node)
        metadata = data.get("metadata", "{}")
        try:
            metadata_dict = json.loads(metadata)
        except (json.JSONDecodeError, TypeError):
            metadata_dict = {}

        return NodeData(
            id=data["id"],
            type=NodeType(data["type"]),
            content=data["content"],
            metadata=metadata_dict,
        )
