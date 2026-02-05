"""Script to relate Team nodes to Architecture and Philosophy concepts."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_dev_graph.application.manager import get_graph_manager
from ai_dev_graph.domain.models import NodeData, NodeType

def relate_team_concepts():
    # Force SQLite if needed, or rely on env
    # os.environ["DATABASE_TYPE"] = "sqlite" 
    
    manager = get_graph_manager()
    kg = manager.load_or_create()
    
    print("Relating Team to Concepts...")

    # Ensure Architecture/SOLID nodes exist (idempotent-ish if we just reference them as parents/children)
    # But kg.add_edge requires both nodes to exist.
    # The previous script `add_clean_arch_solid.py` adds them. Let's assume they might not be there if we just ran init_meta.
    # So I'll quickly re-add the roots just in case, or check.
    
    try:
        kg.repo.get_node("clean_architecture")
    except:
        print("Clean Architecture node not found. Please run add_clean_arch_solid.py first or we will add basics now.")
        # For robustness, let's just add the basic structure if missing
        clean_arch = NodeData(id="clean_architecture", type=NodeType.CONCEPT, content="Clean Architecture")
        kg.add_knowledge(clean_arch, parents=["philosophy"])
        
        solid = NodeData(id="solid_principles", type=NodeType.CONCEPT, content="SOLID Principles")
        kg.add_knowledge(solid, parents=["philosophy"])

    # Define Relationships
    relationships = [
        # Arquitecto es el guardián de la arquitectura y principios
        ("role_arquitecto_sistema", "clean_architecture"),
        ("role_arquitecto_sistema", "solid_principles"),
        ("role_arquitecto_sistema", "philosophy"),
        
        # Backend Core implementa las reglas de dominio y SOLID
        ("role_ing_backend_core", "clean_architecture"),
        ("role_ing_backend_core", "solid_principles"),
        ("role_ing_backend_core", "layer_domain"), # Might fail if layer_domain doesn't exist
        
        # Backend API implementa la capa de aplicación/infra
        ("role_ing_backend_api", "clean_architecture"),
        
        # Testing verifica cumplimiento
        ("role_ing_testing", "solid_principles"),
        
        # Calidad mide deuda técnica (relacionada con mala aplicación de principios)
        ("role_ing_qa", "solid_principles"),
        ("role_ing_qa", "maintenance_policy")
    ]
    
    for role_id, concept_id in relationships:
        try:
            # Access repo via kg.repo
            if kg.repo.get_node(role_id) and kg.repo.get_node(concept_id):
                kg.repo.add_edge(role_id, concept_id)
                print(f"Connected {role_id} -> {concept_id}")
            else:
                print(f"Skipping {role_id} -> {concept_id} (Nodes missing)")
        except Exception as e:
            print(f"Error connecting {role_id} -> {concept_id}: {e}")

    manager.save_with_backup()
    print("Relationships established.")

if __name__ == "__main__":
    relate_team_concepts()
