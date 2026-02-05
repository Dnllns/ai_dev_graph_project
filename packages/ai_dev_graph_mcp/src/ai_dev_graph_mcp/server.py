"""Advanced MCP Server for AI Dev Graph - Enhanced Graph Operations."""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict, deque
import re

from ai_dev_graph.application.manager import GraphManager, get_graph_manager
from ai_dev_graph.waterfall_tracker import WaterfallTracker
from ai_dev_graph.domain.models import NodeType

logger = logging.getLogger(__name__)


class AdvancedMCPServer:
    """Advanced MCP Server with enhanced graph navigation and analysis capabilities."""

    def __init__(self, graph_manager: GraphManager):
        self.graph_manager = graph_manager
        self.kg = graph_manager.load_or_create()
        self.waterfall = WaterfallTracker()

    # ===== ADVANCED GRAPH NAVIGATION =====

    def traverse_graph(
        self,
        start_node: str,
        max_depth: int = 3,
        direction: str = "both",
        node_filter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Traverse the graph from a starting node using BFS.

        Args:
            start_node: Starting node ID
            max_depth: Maximum depth to traverse
            direction: 'forward', 'backward', or 'both'
            node_filter: Optional filter for node types or properties

        Returns:
            Dictionary with traversal results including paths and nodes
        """
        visited = set()
        queue = deque([(start_node, 0, [])])
        paths = []
        nodes_by_depth = defaultdict(list)

        while queue:
            node_id, depth, path = queue.popleft()

            if depth > max_depth or node_id in visited:
                continue

            visited.add(node_id)
            current_path = path + [node_id]

            node_data = self.kg.get_node_data(node_id)
            if not node_data:
                continue

            # Check if node matches filter criteria, but continue traversal regardless
            matches_filter = True
            if node_filter:
                if "type" in node_filter and node_data.type.value != node_filter["type"]:
                    matches_filter = False
                if "content_match" in node_filter:
                    if node_filter["content_match"].lower() not in node_data.content.lower():
                        matches_filter = False

            if matches_filter:
                nodes_by_depth[depth].append(
                    {
                        "id": node_id,
                        "type": node_data.type.value,
                        "content": node_data.content[:200],
                        "metadata": node_data.metadata,
                    }
                )

            if depth == max_depth:
                if matches_filter:
                    paths.append(current_path)
                continue

            # Get neighbors based on direction
            neighbors = []
            if direction in ["forward", "both"]:
                neighbors.extend(self.kg.get_successors(node_id))
            if direction in ["backward", "both"]:
                neighbors.extend(self.kg.get_predecessors(node_id))

            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1, current_path))

        return {
            "start_node": start_node,
            "max_depth": max_depth,
            "nodes_visited": len(visited),
            "paths": paths,
            "nodes_by_depth": dict(nodes_by_depth),
        }

    def find_shortest_path(
        self, source: str, target: str, max_depth: int = 10
    ) -> Optional[List[str]]:
        """Find the shortest path between two nodes using BFS."""
        if source == target:
            return [source]

        visited = {source}
        queue = deque([(source, [source])])

        while queue:
            node, path = queue.popleft()

            if len(path) > max_depth:
                continue

            # Check both successors and predecessors
            neighbors = set(self.kg.get_successors(node)) | set(
                self.kg.get_predecessors(node)
            )

            for neighbor in neighbors:
                if neighbor == target:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def find_all_paths(
        self, source: str, target: str, max_depth: int = 5, max_paths: int = 10
    ) -> List[List[str]]:
        """Find all paths between two nodes up to a maximum depth."""
        paths = []

        def dfs(current: str, target: str, path: List[str], depth: int):
            if len(paths) >= max_paths or depth > max_depth:
                return

            if current == target:
                paths.append(path.copy())
                return

            successors = self.kg.get_successors(current)
            for neighbor in successors:
                if neighbor not in path:  # Avoid cycles
                    path.append(neighbor)
                    dfs(neighbor, target, path, depth + 1)
                    path.pop()

        dfs(source, target, [source], 0)
        return paths

    def get_node_neighborhood(
        self, node_id: str, radius: int = 1
    ) -> Dict[str, Any]:
        """Get the complete neighborhood of a node within a given radius."""
        neighborhood = {
            "center": node_id,
            "radius": radius,
            "nodes": {},
            "edges": [],
        }

        visited = set()
        queue = deque([(node_id, 0)])

        while queue:
            current, depth = queue.popleft()

            if current in visited or depth > radius:
                continue

            visited.add(current)
            node_data = self.kg.get_node_data(current)

            if node_data:
                neighborhood["nodes"][current] = {
                    "type": node_data.type.value,
                    "content": node_data.content,
                    "metadata": node_data.metadata,
                    "depth": depth,
                }

            # Get all edges
            successors = self.kg.get_successors(current)
            predecessors = self.kg.get_predecessors(current)

            for succ in successors:
                neighborhood["edges"].append(
                    {"source": current, "target": succ, "direction": "forward"}
                )
                if depth < radius:
                    queue.append((succ, depth + 1))

            for pred in predecessors:
                neighborhood["edges"].append(
                    {"source": pred, "target": current, "direction": "backward"}
                )
                if depth < radius:
                    queue.append((pred, depth + 1))

        return neighborhood

    # ===== ADVANCED SEARCH =====

    def semantic_search(
        self,
        query: str,
        node_types: Optional[List[str]] = None,
        limit: int = 20,
        include_metadata: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Advanced semantic search with scoring and ranking.

        Scoring factors:
        - Exact match bonus
        - Word match count
        - Position of match (earlier is better)
        - Node type relevance
        """
        query_lower = query.lower()
        query_words = set(re.findall(r"\w+", query_lower))

        filters = {}
        if node_types:
            # Search across multiple types
            all_results = []
            for node_type in node_types:
                filters["type"] = node_type
                node_ids = self.kg.find_nodes(**filters)
                all_results.extend(node_ids)
        else:
            node_ids = self.kg.find_nodes()
            all_results = node_ids

        scored_results = []

        for node_id in all_results:
            node = self.kg.get_node_data(node_id)
            if not node:
                continue

            content_lower = node.content.lower()
            score = 0

            # Exact match bonus
            if query_lower in content_lower:
                score += 100
                # Position bonus (earlier matches score higher)
                position = content_lower.find(query_lower)
                score += max(0, 50 - position)

            # Word match scoring
            content_words = set(re.findall(r"\w+", content_lower))
            matching_words = query_words & content_words
            score += len(matching_words) * 10

            # Metadata search bonus
            if include_metadata and node.metadata:
                metadata_str = str(node.metadata).lower()
                if query_lower in metadata_str:
                    score += 20

            # Node type relevance
            if node.type == NodeType.CONCEPT:
                score += 5
            elif node.type == NodeType.RULE:
                score += 3

            if score > 0:
                result = {
                    "id": node_id,
                    "type": node.type.value,
                    "content": node.content,
                    "score": score,
                    "parents": self.kg.get_predecessors(node_id),
                    "children": self.kg.get_successors(node_id),
                }

                if include_metadata:
                    result["metadata"] = node.metadata

                scored_results.append(result)

        # Sort by score and limit results
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:limit]

    def find_related_nodes(
        self, node_id: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Find nodes related to a given node based on graph structure and content."""
        node = self.kg.get_node_data(node_id)
        if not node:
            return []

        # Get direct neighbors
        direct_neighbors = set(self.kg.get_successors(node_id)) | set(
            self.kg.get_predecessors(node_id)
        )

        # Get second-degree neighbors
        second_degree = set()
        for neighbor in direct_neighbors:
            second_degree.update(self.kg.get_successors(neighbor))
            second_degree.update(self.kg.get_predecessors(neighbor))

        # Remove the original node and direct neighbors
        second_degree -= {node_id}
        second_degree -= direct_neighbors

        # Score based on shared neighbors
        scores = {}
        for candidate in second_degree:
            candidate_neighbors = set(self.kg.get_successors(candidate)) | set(
                self.kg.get_predecessors(candidate)
            )
            shared = direct_neighbors & candidate_neighbors
            scores[candidate] = len(shared)

        # Sort and get top results
        sorted_candidates = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for candidate_id, score in sorted_candidates[:max_results]:
            candidate_node = self.kg.get_node_data(candidate_id)
            if candidate_node:
                results.append(
                    {
                        "id": candidate_id,
                        "type": candidate_node.type.value,
                        "content": candidate_node.content[:200],
                        "relatedness_score": score,
                        "shared_neighbors": score,
                    }
                )

        return results

    # ===== LINK PREDICTION =====

    def predict_missing_links(
        self, min_score: float = 0.3, max_predictions: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Predict missing links in the graph using common neighbors and content similarity.
        """
        all_nodes = self.kg.repo.get_all_nodes()
        predictions = []

        for i, node1 in enumerate(all_nodes):
            for node2 in all_nodes[i + 1 :]:
                # Skip if already connected
                if node2.id in self.kg.get_successors(node1.id):
                    continue
                if node1.id in self.kg.get_successors(node2.id):
                    continue

                score = self._calculate_link_score(node1.id, node2.id)

                if score >= min_score:
                    predictions.append(
                        {
                            "source": node1.id,
                            "target": node2.id,
                            "score": round(score, 3),
                            "source_type": node1.type.value,
                            "target_type": node2.type.value,
                            "reason": self._explain_prediction(node1.id, node2.id),
                        }
                    )

        # Sort by score and limit
        predictions.sort(key=lambda x: x["score"], reverse=True)
        return predictions[:max_predictions]

    def _calculate_link_score(self, node1_id: str, node2_id: str) -> float:
        """Calculate the probability of a link between two nodes."""
        score = 0.0

        # Common neighbors (Jaccard coefficient)
        neighbors1 = set(self.kg.get_successors(node1_id)) | set(
            self.kg.get_predecessors(node1_id)
        )
        neighbors2 = set(self.kg.get_successors(node2_id)) | set(
            self.kg.get_predecessors(node2_id)
        )

        if neighbors1 or neighbors2:
            common = len(neighbors1 & neighbors2)
            total = len(neighbors1 | neighbors2)
            score += (common / total) * 0.5 if total > 0 else 0

        # Content similarity (simple word overlap)
        node1 = self.kg.get_node_data(node1_id)
        node2 = self.kg.get_node_data(node2_id)

        if node1 and node2:
            words1 = set(re.findall(r"\w+", node1.content.lower()))
            words2 = set(re.findall(r"\w+", node2.content.lower()))

            if words1 or words2:
                common_words = len(words1 & words2)
                total_words = len(words1 | words2)
                score += (common_words / total_words) * 0.3 if total_words > 0 else 0

            # Type compatibility bonus
            if node1.type == node2.type:
                score += 0.1
            elif (
                node1.type == NodeType.CONCEPT and node2.type == NodeType.GUIDELINE
            ) or (node1.type == NodeType.GUIDELINE and node2.type == NodeType.CONCEPT):
                score += 0.1

        return min(score, 1.0)

    def _explain_prediction(self, node1_id: str, node2_id: str) -> str:
        """Generate an explanation for a link prediction."""
        neighbors1 = set(self.kg.get_successors(node1_id)) | set(
            self.kg.get_predecessors(node1_id)
        )
        neighbors2 = set(self.kg.get_successors(node2_id)) | set(
            self.kg.get_predecessors(node2_id)
        )
        common = neighbors1 & neighbors2

        if common:
            return f"Share {len(common)} common neighbors: {', '.join(list(common)[:3])}"
        return "Similar content and type compatibility"

    def suggest_new_links(
        self, node_id: str, max_suggestions: int = 5
    ) -> List[Dict[str, Any]]:
        """Suggest new links for a specific node."""
        node = self.kg.get_node_data(node_id)
        if not node:
            return []

        all_nodes = self.kg.repo.get_all_nodes()
        suggestions = []

        existing_links = set(self.kg.get_successors(node_id)) | set(
            self.kg.get_predecessors(node_id)
        )

        for candidate in all_nodes:
            if candidate.id == node_id or candidate.id in existing_links:
                continue

            score = self._calculate_link_score(node_id, candidate.id)

            if score > 0.2:
                suggestions.append(
                    {
                        "target": candidate.id,
                        "target_type": candidate.type.value,
                        "target_content": candidate.content[:100],
                        "score": round(score, 3),
                        "reason": self._explain_prediction(node_id, candidate.id),
                    }
                )

        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions[:max_suggestions]

    # ===== GRAPH ANALYSIS =====

    def analyze_node_importance(self) -> List[Dict[str, Any]]:
        """Analyze node importance using degree centrality and PageRank-like scoring."""
        all_nodes = self.kg.repo.get_all_nodes()
        importance_scores = []

        for node in all_nodes:
            in_degree = len(self.kg.get_predecessors(node.id))
            out_degree = len(self.kg.get_successors(node.id))
            total_degree = in_degree + out_degree

            # Simple importance score
            score = total_degree * 10

            # Bonus for certain types
            if node.type == NodeType.CONCEPT:
                score += 5
            elif node.type == NodeType.GUIDELINE:
                score += 3

            importance_scores.append(
                {
                    "id": node.id,
                    "type": node.type.value,
                    "content": node.content[:100],
                    "importance_score": score,
                    "in_degree": in_degree,
                    "out_degree": out_degree,
                }
            )

        importance_scores.sort(key=lambda x: x["importance_score"], reverse=True)
        return importance_scores

    def detect_communities(self) -> Dict[str, List[str]]:
        """Detect communities/clusters in the graph using simple connected components."""
        all_nodes = [node.id for node in self.kg.repo.get_all_nodes()]
        visited = set()
        communities = {}
        community_id = 0

        def dfs(node_id: str, community: List[str]):
            if node_id in visited:
                return
            visited.add(node_id)
            community.append(node_id)

            neighbors = set(self.kg.get_successors(node_id)) | set(
                self.kg.get_predecessors(node_id)
            )
            for neighbor in neighbors:
                dfs(neighbor, community)

        for node_id in all_nodes:
            if node_id not in visited:
                community = []
                dfs(node_id, community)
                if community:
                    communities[f"community_{community_id}"] = community
                    community_id += 1

        return communities

    def get_graph_metrics(self) -> Dict[str, Any]:
        """Get comprehensive graph metrics."""
        all_nodes = self.kg.repo.get_all_nodes()
        all_edges = self.kg.repo.get_all_edges()

        node_types = defaultdict(int)
        for node in all_nodes:
            node_types[node.type.value] += 1

        # Calculate average degree
        degrees = []
        for node in all_nodes:
            degree = len(self.kg.get_successors(node.id)) + len(
                self.kg.get_predecessors(node.id)
            )
            degrees.append(degree)

        avg_degree = sum(degrees) / len(degrees) if degrees else 0

        return {
            "total_nodes": len(all_nodes),
            "total_edges": len(all_edges),
            "node_types": dict(node_types),
            "average_degree": round(avg_degree, 2),
            "max_degree": max(degrees) if degrees else 0,
            "min_degree": min(degrees) if degrees else 0,
            "density": (
                len(all_edges) / (len(all_nodes) * (len(all_nodes) - 1))
                if len(all_nodes) > 1
                else 0
            ),
        }

    # ===== LEGACY METHODS (for compatibility) =====

    def get_node(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get node with context (legacy method)."""
        return self.kg.get_context(node_id, depth=depth)

    def search_nodes(
        self, query: str, node_type: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search nodes (legacy method, now uses semantic search)."""
        node_types = [node_type] if node_type else None
        return self.semantic_search(query, node_types=node_types, limit=limit)

    def get_coding_standards(self) -> Dict[str, Any]:
        """Get coding standards from the graph."""
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

    def export_for_agent(self, agent_type: str = "claude") -> Dict[str, Any]:
        """Export graph data optimized for AI agents."""
        return {
            "meta": {
                "export_time": datetime.now().isoformat(),
                "agent_type": agent_type,
                "graph_version": "advanced_v2",
            },
            "graph_metrics": self.get_graph_metrics(),
            "important_nodes": self.analyze_node_importance()[:10],
            "standards": self.get_coding_standards(),
            "communities": self.detect_communities(),
        }


_advanced_mcp_instance = None


def get_advanced_mcp_server() -> AdvancedMCPServer:
    """Get or create the advanced MCP server instance."""
    global _advanced_mcp_instance
    if _advanced_mcp_instance is None:
        manager = get_graph_manager()
        _advanced_mcp_instance = AdvancedMCPServer(manager)
    return _advanced_mcp_instance
