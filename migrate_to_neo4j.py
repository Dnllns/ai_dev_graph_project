"""Script to migrate existing SQLite graph to Neo4j (via Hybrid approach).

This pushes the structure of the graph currently in SQLite to Neo4j.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_dev_graph.infrastructure.persistence_factory import PersistenceFactory
from ai_dev_graph.core.config import settings, DatabaseType
from ai_dev_graph.infrastructure.hybrid_repo import HybridRepository

def migrate():
    # Force Hybrid mode
    settings.database_type = DatabaseType.HYBRID
    
    # Reset factory to pick up new setting
    PersistenceFactory.reset()
    
    try:
        repo = PersistenceFactory.get_repository()
    except Exception as e:
        print(f"Failed to initialize repository: {e}")
        return

    if not isinstance(repo, HybridRepository):
        print("Error: Repository is not HybridRepository. Check configuration.")
        return

    print("Starting migration to Neo4j...")
    
    # 1. Get all nodes from SQLite
    nodes = repo.sqlite.get_all_nodes()
    print(f"Found {len(nodes)} nodes in SQLite.")
    
    # 2. Get all edges from SQLite
    edges = repo.sqlite.get_all_edges()
    print(f"Found {len(edges)} edges in SQLite.")
    
    # 3. Push Nodes to Neo4j
    # We call add_node on the Neo4j component directly to avoid re-writing to SQLite
    count = 0
    for node_data in nodes:
        # We need to construct NodeData objects because Neo4jRepo expects them
        # node_data is a dict here from the sqlite.get_all_nodes() call
        from ai_dev_graph.domain.models import NodeData, NodeType
        
        nd = NodeData(
            id=node_data["id"],
            type=NodeType(node_data["type"]),
            content=node_data["content"],
            metadata=node_data["metadata"]
        )
        
        try:
            repo.neo4j.add_node(nd)
            count += 1
            if count % 10 == 0:
                print(f"Migrated {count} nodes...", end="\r")
        except Exception as e:
            print(f"Failed to migrate node {nd.id}: {e}")
            
    print(f"\nNodes migration complete. {count}/{len(nodes)} synced.")
    
    # 4. Push Edges to Neo4j
    count = 0
    for source, target in edges:
        try:
            repo.neo4j.add_edge(source, target)
            count += 1
            if count % 10 == 0:
                print(f"Migrated {count} edges...", end="\r")
        except Exception as e:
            print(f"Failed to migrate edge {source}->{target}: {e}")

    print(f"\nEdges migration complete. {count}/{len(edges)} synced.")
    
    print("Migration finished successfully.")

if __name__ == "__main__":
    migrate()
