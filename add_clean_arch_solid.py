"""Script to add Clean Architecture and SOLID principles to the knowledge graph."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_dev_graph.domain.graph import KnowledgeGraph
from ai_dev_graph.domain.models import NodeData, NodeType
from ai_dev_graph.application.manager import get_graph_manager


def add_clean_architecture_and_solid():
    """Add Clean Architecture and SOLID principles nodes to the graph."""
    
    manager = get_graph_manager()
    kg = manager.load_or_create()
    
    print("Adding Clean Architecture and SOLID Principles...\n")
    
    # === CLEAN ARCHITECTURE ===
    
    clean_arch = NodeData(
        id="clean_architecture",
        type=NodeType.CONCEPT,
        content="Clean Architecture: layering system for separation of concerns. Domain at center. Dependencies point inward."
    )
    kg.add_knowledge(clean_arch, parents=["philosophy"])
    
    layers = [
        {"id": "layer_domain", "content": "DOMAIN LAYER: entities, value objects, pure logic. No external dependencies."},
        {"id": "layer_application", "content": "APPLICATION LAYER: use cases, app services. Orchestrates domain. Defines interfaces."},
        {"id": "layer_infrastructure", "content": "INFRASTRUCTURE LAYER: persistence, external APIs, frameworks implementation."},
        {"id": "layer_presentation", "content": "PRESENTATION LAYER: UI, API controllers, request/response conversion."}
    ]
    
    for layer in layers:
        kg.add_knowledge(NodeData(id=layer["id"], type=NodeType.CONCEPT, content=layer["content"]), parents=["clean_architecture"])
    
    clean_rules = [
        {"id": "rule_dependency_inversion", "content": "RULE: External layers depend on internal. Never vice versa. Use interfaces."},
        {"id": "rule_no_framework_in_domain", "content": "RULE: Domain must not depend on frameworks like FastAPI or SQLAlchemy."},
        {"id": "rule_single_responsibility_layer", "content": "RULE: Each layer has ONE responsibility. Domain: logic. App: use cases. Infra: tech."}
    ]
    
    for rule in clean_rules:
        kg.add_knowledge(NodeData(id=rule["id"], type=NodeType.RULE, content=rule["content"]), parents=["clean_architecture"])
    
    # === SOLID PRINCIPLES ===
    
    solid = NodeData(
        id="solid_principles",
        type=NodeType.CONCEPT,
        content="SOLID: five design principles for maintainable and scalable software."
    )
    kg.add_knowledge(solid, parents=["philosophy"])
    
    principles = [
        {"id": "principle_srp", "name": "SRP", "content": "Single Responsibility Principle. A class should have one reason to change."},
        {"id": "principle_ocp", "name": "OCP", "content": "Open/Closed Principle. Open for extension, closed for modification."},
        {"id": "principle_lsp", "name": "LSP", "content": "Liskov Substitution Principle. Subtypes must be substitutable for base types."},
        {"id": "principle_isp", "name": "ISP", "content": "Interface Segregation Principle. Many specific interfaces better than one general."},
        {"id": "principle_dip", "name": "DIP", "content": "Dependency Inversion Principle. Depend on abstractions, not concretions."}
    ]
    
    for p in principles:
        kg.add_knowledge(NodeData(id=p["id"], type=NodeType.CONCEPT, content=f"{p['name']}: {p['content']}"), parents=["solid_principles"])
    
    # === EXAMPLES ===
    
    examples = NodeData(
        id="architecture_examples",
        type=NodeType.CONCEPT,
        content="EXAMPLES: Domain (domain/graph.py), Application (application/manager.py), Infrastructure (infrastructure/networkx_repo.py)."
    )
    kg.add_knowledge(examples, parents=["clean_architecture", "solid_principles"])
    
    manager.save_with_backup()
    print("Clean Architecture and SOLID principles added successfully!")


if __name__ == "__main__":
    add_clean_architecture_and_solid()
