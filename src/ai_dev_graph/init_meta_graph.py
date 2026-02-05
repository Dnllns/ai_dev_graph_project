from ai_dev_graph.domain.graph import KnowledgeGraph
from ai_dev_graph.domain.models import NodeData, NodeType
from ai_dev_graph.infrastructure.persistence_factory import PersistenceFactory
from ai_dev_graph.domain.repositories import GraphRepository
from pathlib import Path
import os
import json
import logging

logger = logging.getLogger(__name__)

def init_project_graph(storage_dir: str = "graphs", use_db: bool = True, repository: GraphRepository = None):
    """
    Initialize the project knowledge graph with core philosophy and standards.
    """
    repo = repository or PersistenceFactory.get_repository()
    kg = KnowledgeGraph(repository=repo)
    
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
    
    # --- EQUIPO DE CONSTRUCCIÓN ---
    # Implementación del documento de organización del equipo
    
    # Nodo Raíz del Equipo
    team_root = NodeData(
        id="equipo_construccion",
        type=NodeType.CONCEPT,
        content="Equipo de Construcción de Software. Organización jerárquica basada en dominio y conocimiento para eliminar ambigüedad.",
        metadata={"document": "equipo_de_construccion_software"}
    )
    kg.add_knowledge(team_root, parents=["ai_dev_graph"])

    # Principios
    principios = NodeData(
        id="team_principles",
        type=NodeType.RULE,
        content="Principios Generales: 1. No todos opinan sobre todo. 2. Autoridad depende del dominio. 3. Decisiones lo más cerca posible del problema. 4. Conocimiento fluye arriba, decisiones abajo."
    )
    kg.add_knowledge(principios, parents=["equipo_construccion"])

    # Regla de Oro
    golden_rule = NodeData(
        id="team_golden_rule",
        type=NodeType.RULE,
        content="REGLA DE ORO: Nadie manda sobre lo que no entiende y nadie implementa lo que no ha sido decidido."
    )
    kg.add_knowledge(golden_rule, parents=["equipo_construccion", "team_principles"])

    # Orden de Comunicación
    comm_order = NodeData(
        id="team_comm_order",
        type=NodeType.RULE,
        content="Orden de Comunicación: 1. Experto del dominio (habla primero). 2. Coordinador Técnico (encaja decisión). 3. Arquitecto de Sistema (resuelve conflictos/impacto global). 4. Resto (escucha/ejecuta)."
    )
    kg.add_knowledge(comm_order, parents=["equipo_construccion"])

    # --- ROLES ---

    # 1. Arquitecto
    architect = NodeData(
        id="role_arquitecto_sistema",
        type=NodeType.CONCEPT,
        content="Arquitecto de Sistema: Máxima autoridad técnica. Decide arquitectura global, resuelve conflictos y tiene la última palabra estructural. NO implementa detalles.",
        metadata={"priority": 1, "scope": "global"}
    )
    kg.add_knowledge(architect, parents=["equipo_construccion"])

    # 2. Coordinador
    coordinator = NodeData(
        id="role_coordinador_tecnico",
        type=NodeType.CONCEPT,
        content="Coordinador Técnico: Autoridad operativa. Decide prioridades, coordina dependencias y traduce objetivos. Escala al Arquitecto.",
        metadata={"priority": 2, "scope": "operational"}
    )
    kg.add_knowledge(coordinator, parents=["equipo_construccion"])

    # 3. Responsables de Dominio (Grupo)
    domain_leads = NodeData(
        id="role_group_domain_leads",
        type=NodeType.CONCEPT,
        content="Responsables de Dominio: Autoridad total dentro de su área. Nadie fuera del dominio decide por ellos."
    )
    kg.add_knowledge(domain_leads, parents=["equipo_construccion"])

    # Definición de Roles Específicos
    roles_specs = [
        ("role_ing_backend_core", "Ingeniero Backend Core", "reglas de negocio"),
        ("role_ing_backend_api", "Ingeniero Backend API", "contratos y apis"),
        ("role_ing_frontend_core", "Ingeniero Frontend Core", "experiencia de usuario"),
        ("role_ing_frontend_int", "Ingeniero Frontend Integración", "integracion ui backend"),
        ("role_ing_datos", "Ingeniero de Datos", "modelo de datos y persistencia"),
        ("role_ing_grafos", "Ingeniero de Grafos", "relaciones complejas y conocimiento conectado"),
        ("role_ing_ia_sistemas", "Ingeniero IA Sistemas", "comportamiento, memoria, contexto y control de IA"),
        ("role_ing_ia_int", "Ingeniero IA Integración", "integración de modelos IA"),
        ("role_ing_seguridad", "Ingeniero Seguridad", "seguridad end-to-end y cumplimiento"),
        ("role_ing_infra", "Ingeniero Infraestructura", "estabilidad, física y red"),
        ("role_ing_devops", "Ingeniero DevOps", "despliegue y operación"),
        ("role_ing_testing", "Ingeniero Testing", "pruebas"),
        ("role_ing_qa", "Ingeniero Calidad", "calidad y deuda técnica"),
        ("role_ing_obs", "Ingeniero Observabilidad", "logs, métricas, alertas"),
        ("role_ing_docs", "Ingeniero Documentación", "documentación"),
        ("role_ing_version", "Ingeniero Versionado", "versionado y releases"),
        ("role_ing_auto", "Ingeniero Automatización", "automatización"),
        ("role_ing_interop", "Ingeniero Interoperabilidad", "integraciones externas"),
    ]

    for rid, rname, rscope in roles_specs:
        node = NodeData(
            id=rid,
            type=NodeType.CONCEPT,
            content=f"{rname}: Experto en {rscope}. Autoridad en su dominio.",
            metadata={"role_name": rname, "domain_scope": rscope}
        )
        kg.add_knowledge(node, parents=["role_group_domain_leads"])

    logger.info("Equipo de construcción añadido al grafo.")

    # Persist artifact JSON for compliance and tests (Generic implementation)
    storage_path = Path(storage_dir)
    storage_path.mkdir(parents=True, exist_ok=True)
    
    nodes_data = [node.model_dump() for node in repo.get_all_nodes()]
    links_data = [{"source": u, "target": v} for u, v in repo.get_all_edges()]
    
    data = {
        "directed": True,
        "multigraph": False,
        "graph": {},
        "nodes": nodes_data,
        "links": links_data
    }
    
    with open(storage_path / "v0_initial.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
            
    return kg

if __name__ == "__main__":
    init_project_graph()
