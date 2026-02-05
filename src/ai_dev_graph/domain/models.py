from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any


class NodeType(str, Enum):
    PROJECT = "project"  # Nodo raíz
    CONCEPT = "concept"  # Ideas abstractas o filosofías
    RULE = "rule"  # Obligatorio (MUST)
    GUIDELINE = "guideline"  # Recomendado (SHOULD)
    INSTRUCTION = "instruction"  # Tarea específica
    RESOURCE = "resource"  # Archivos, herramientas
    TEST = "test"  # Criterios de validación


class NodeData(BaseModel):
    id: str
    type: NodeType
    content: str
    metadata: Dict[str, Any] = {}
