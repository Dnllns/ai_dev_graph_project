import pytest
import json
import networkx as nx
from pathlib import Path
from ai_dev_graph.domain.models import NodeType

GRAPH_PATH = Path("graphs/v0_initial.json")


@pytest.fixture
def graph_data():
    """Carga el artefacto del grafo real."""
    if not GRAPH_PATH.exists():
        pytest.fail(
            f"El artefacto {GRAPH_PATH} no existe. Ejecuta 'python -m ai_dev_graph.init_meta_graph'"
        )

    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_graph_is_connected(graph_data):
    """Regla Inquebrantable 1: No puede haber conocimiento aislado (islas)."""
    g = nx.node_link_graph(graph_data)
    if len(g.nodes) > 0:
        # Verifica que el grafo sea débilmente conexo (todo se conecta con todo ignorando dirección)
        assert nx.is_weakly_connected(g), (
            "El grafo de conocimiento está fragmentado (hay nodos inalcanzables)."
        )


def test_taxonomy_compliance(graph_data):
    """Regla Inquebrantable 2: Todos los nodos deben tener un tipo válido."""
    g = nx.node_link_graph(graph_data)
    valid_types = set(item.value for item in NodeType)

    for node_id, attrs in g.nodes(data=True):
        # NetworkX guarda los atributos del nodo dentro de 'data' o planos según serialización
        # Nuestro formato guarda en 'data'
        node_payload = attrs.get("data", {})
        node_type = node_payload.get("type")

        assert node_type is not None, f"El nodo {node_id} no tiene tipo definido."
        assert node_type in valid_types, (
            f"El nodo {node_id} tiene un tipo inválido: {node_type}"
        )


def test_content_is_raw_and_clean(graph_data):
    """Regla Inquebrantable 3: Contenido RAW. Sin emojis, sin ruido, token-efficient."""
    g = nx.node_link_graph(graph_data)

    # Rangos Unicode comunes para emojis y símbolos gráficos
    emoji_ranges = [
        (0x1F600, 0x1F64F),  # Emoticons
        (0x1F300, 0x1F5FF),  # Symbols & Pictographs
        (0x1F680, 0x1F6FF),  # Transport & Map
        (0x2700, 0x27BF),  # Dingbats
        (0x1F900, 0x1F9FF),  # Supplemental Symbols
    ]

    for node_id, attrs in g.nodes(data=True):
        content = attrs.get("data", {}).get("content", "")
        for start, end in emoji_ranges:
            for char in content:
                if start <= ord(char) <= end:
                    pytest.fail(
                        f"VIOLACIÓN DE POLÍTICA RAW: El nodo '{node_id}' contiene emoji/símbolo '{char}'."
                    )
