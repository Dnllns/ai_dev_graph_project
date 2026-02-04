from ai_dev_graph.core.graph import KnowledgeGraph, NodeData, NodeType
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

def init_project_graph(storage_dir: str = "graphs", use_db: bool = True):
    """
    Initialize the project knowledge graph with core philosophy and standards.
    
    Args:
        storage_dir: Directory where the graph will be saved.
        use_db: Use database persistence (default: True).

    Returns:
        KnowledgeGraph: The initialized knowledge graph instance.
    """
    kg = KnowledgeGraph(use_db=use_db)
    
    # Nodo Raíz: El Proyecto
    root = NodeData(
        id="ai_dev_graph",
        type=NodeType.PROJECT,
        content="Herramienta de almacenamiento de conocimiento para agentes IA en forma de grafo."
    )
    kg.add_knowledge(root)

    # Filosofía
    phil = NodeData(
        id="philosophy",
        type=NodeType.CONCEPT,
        content="GRAFO, PYTHON, API, DOC, TEST."
    )
    kg.add_knowledge(phil, parents=["ai_dev_graph"])

    # Estándares de Código
    standards = NodeData(
        id="coding_standards",
        type=NodeType.RULE,
        content="Uso de Python tipado, Pydantic para modelos y NetworkX para el grafo."
    )
    kg.add_knowledge(standards, parents=["philosophy"])

    # Gestión
    git_cz = NodeData(
        id="version_control",
        type=NodeType.RULE,
        content="Uso obligatorio de Git y Commitizen para gestión de estados y changelogs."
    )
    kg.add_knowledge(git_cz, parents=["ai_dev_graph"])

    # Regla: Testing Obligatorio (Consolidado)
    test_rule = NodeData(
        id="rule_must_test",
        type=NodeType.RULE,
        content="Todo código nuevo debe incluir tests automáticos que validen su funcionamiento. No se acepta código sin tests."
    )
    kg.add_knowledge(test_rule, parents=["coding_standards"])

    # Regla: Contenido RAW (Consolidado)
    raw_rule = NodeData(
        id="rule_raw_content",
        type=NodeType.RULE,
        content="Content must be raw text. No emojis. No fluff. High information density. Optimal for LLM consumption."
    )
    kg.add_knowledge(raw_rule, parents=["philosophy"])

    # Nueva Metodología: Mantenimiento del Codebase
    maintenance = NodeData(
        id="maintenance_policy",
        type=NodeType.RULE,
        content="Limpieza proactiva: eliminar código no usado inmediatamente. Mantener el grafo sincronizado con la realidad del código."
    )
    kg.add_knowledge(maintenance, parents=["ai_dev_graph"])

    # Instrucción para Agentes
    agent_inst = NodeData(
        id="agent_instruction",
        type=NodeType.INSTRUCTION,
        content="Los agentes deben consultar el grafo antes de cada tarea para asegurar coherencia con la arquitectura y estándares."
    )
    kg.add_knowledge(agent_inst, parents=["philosophy"])

    # Regla de Calidad: Solo nodos valiosos
    quality_rule = NodeData(
        id="rule_node_quality",
        type=NodeType.RULE,
        content="Solo añadir nodos que aporten valor real al grafo. Evitar nodos redundantes o temporales de testing. Cada nodo debe documentar conocimiento persistente y relevante."
    )
    kg.add_knowledge(quality_rule, parents=["maintenance_policy"])

    logger.info("Grafo meta-inicializado con la filosofía y metodología extendida.")

    # Persistencia del artefacto
    storage_path = Path(storage_dir)
    storage_path.mkdir(parents=True, exist_ok=True)
    kg.save(str(storage_path / "v0_initial.json"))
    return kg

if __name__ == "__main__":
    init_project_graph()
