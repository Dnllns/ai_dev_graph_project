# Advanced MCP Server - Capacidades Mejoradas

## 🚀 Resumen

El MCP Server ha sido significativamente mejorado con capacidades avanzadas de navegación, búsqueda, predicción y análisis del grafo de conocimiento. Estas mejoras permiten a los agentes de IA interactuar de manera mucho más sofisticada con el grafo.

## 📊 Nuevas Capacidades

### 1. **Navegación Avanzada del Grafo**

#### Traversal (Recorrido) del Grafo
```python
from ai_dev_graph.advanced_mcp import get_advanced_mcp_server

mcp = get_advanced_mcp_server()

# Recorrer el grafo desde un nodo
result = mcp.traverse_graph(
    start_node="philosophy",
    max_depth=3,
    direction="both",  # 'forward', 'backward', or 'both'
    node_filter={"type": "concept"}
)

print(f"Nodos visitados: {result['nodes_visited']}")
print(f"Nodos por profundidad: {result['nodes_by_depth']}")
```

#### Búsqueda de Caminos
```python
# Camino más corto entre dos nodos
path = mcp.find_shortest_path("clean_architecture", "testing_strategy")
print(f"Camino: {' → '.join(path)}")

# Todos los caminos posibles
all_paths = mcp.find_all_paths("source", "target", max_depth=5, max_paths=10)
for i, path in enumerate(all_paths, 1):
    print(f"Camino {i}: {' → '.join(path)}")
```

#### Vecindario de Nodos
```python
# Obtener todos los nodos en un radio específico
neighborhood = mcp.get_node_neighborhood("coding_standards", radius=2)
print(f"Nodos encontrados: {len(neighborhood['nodes'])}")
print(f"Conexiones: {len(neighborhood['edges'])}")
```

### 2. **Búsqueda Semántica Avanzada**

#### Búsqueda con Scoring Inteligente
```python
# Búsqueda semántica con puntuación
results = mcp.semantic_search(
    query="clean architecture principles",
    node_types=["concept", "guideline"],
    limit=10,
    include_metadata=True
)

for result in results:
    print(f"Score: {result['score']} - {result['id']}")
    print(f"  {result['content'][:100]}...")
```

**Factores de Puntuación:**
- ✅ Coincidencia exacta (+100 puntos)
- ✅ Posición del match (antes es mejor, +50 puntos)
- ✅ Palabras coincidentes (+10 por palabra)
- ✅ Metadata match (+20 puntos)
- ✅ Relevancia por tipo de nodo (+3-5 puntos)

#### Nodos Relacionados
```python
# Encontrar nodos relacionados por estructura del grafo
related = mcp.find_related_nodes("waterfall_methodology", max_results=5)

for node in related:
    print(f"{node['id']}: {node['relatedness_score']} vecinos compartidos")
```

### 3. **Predicción de Enlaces**

#### Predecir Enlaces Faltantes
```python
# Descubrir conexiones potenciales en el grafo
predictions = mcp.predict_missing_links(min_score=0.3, max_predictions=20)

for pred in predictions:
    print(f"Score: {pred['score']:.3f}")
    print(f"  {pred['source']} → {pred['target']}")
    print(f"  Razón: {pred['reason']}")
```

**Algoritmos de Predicción:**
- 🔗 Coeficiente de Jaccard (vecinos comunes)
- 📝 Similitud de contenido (overlap de palabras)
- 🏷️ Compatibilidad de tipos de nodo

#### Sugerir Enlaces para un Nodo
```python
# Sugerencias específicas para un nodo
suggestions = mcp.suggest_new_links("test_driven_development", max_suggestions=5)

for sugg in suggestions:
    print(f"{sugg['target']} ({sugg['target_type']})")
    print(f"  Score: {sugg['score']:.3f}")
    print(f"  {sugg['reason']}")
```

### 4. **Análisis del Grafo**

#### Importancia de Nodos
```python
# Ranking de nodos por importancia
importance = mcp.analyze_node_importance()

for node in importance[:10]:  # Top 10
    print(f"{node['id']}: {node['importance_score']}")
    print(f"  In: {node['in_degree']}, Out: {node['out_degree']}")
```

**Métricas de Importancia:**
- 📊 Grado total (in + out degree)
- 🎯 Bonus por tipo de nodo
- 🔝 Ordenado por relevancia

#### Detección de Comunidades
```python
# Identificar clusters/comunidades en el grafo
communities = mcp.detect_communities()

for community_id, nodes in communities.items():
    print(f"{community_id}: {len(nodes)} nodos")
    print(f"  {', '.join(nodes[:5])}...")
```

#### Métricas Globales
```python
# Estadísticas comprehensivas del grafo
metrics = mcp.get_graph_metrics()

print(f"Total de nodos: {metrics['total_nodes']}")
print(f"Total de aristas: {metrics['total_edges']}")
print(f"Grado promedio: {metrics['average_degree']:.2f}")
print(f"Densidad: {metrics['density']:.4f}")
print(f"Tipos de nodos: {metrics['node_types']}")
```

## 🎨 CLI Avanzado con Rich UI

### Comandos Disponibles

```bash
# Recorrer el grafo
python -m ai_dev_graph.cli_graph traverse philosophy --depth 3 --direction both

# Encontrar caminos
python -m ai_dev_graph.cli_graph path clean_architecture testing_strategy
python -m ai_dev_graph.cli_graph path source target --all --max-paths 5

# Ver vecindario
python -m ai_dev_graph.cli_graph neighborhood coding_standards --radius 2

# Búsqueda semántica
python -m ai_dev_graph.cli_graph search "clean architecture" --type concept --limit 10

# Nodos relacionados
python -m ai_dev_graph.cli_graph related waterfall_methodology --limit 10

# Predicción de enlaces
python -m ai_dev_graph.cli_graph predict-links --min-score 0.3 --limit 20
python -m ai_dev_graph.cli_graph suggest-links test_driven_development --limit 5

# Análisis
python -m ai_dev_graph.cli_graph importance --limit 20
python -m ai_dev_graph.cli_graph communities
python -m ai_dev_graph.cli_graph metrics

# Exportar como JSON
python -m ai_dev_graph.cli_graph search "architecture" --json > results.json
```

### Características del CLI

- 🎨 **Rich Terminal UI**: Tablas, árboles y paneles coloridos
- 📊 **Visualizaciones**: Representaciones claras de datos complejos
- 💾 **Export JSON**: Todos los comandos soportan `--json`
- 🔍 **Filtros Avanzados**: Por tipo, profundidad, score, etc.

## 🧪 Tests

El proyecto incluye una suite comprehensiva de tests:

```bash
# Ejecutar todos los tests del MCP avanzado
uv run pytest tests/test_advanced_mcp.py -v

# Tests específicos
uv run pytest tests/test_advanced_mcp.py::TestGraphTraversal -v
uv run pytest tests/test_advanced_mcp.py::TestSemanticSearch -v
uv run pytest tests/test_advanced_mcp.py::TestLinkPrediction -v
uv run pytest tests/test_advanced_mcp.py::TestGraphAnalysis -v
```

**Cobertura de Tests:**
- ✅ Navegación del grafo (traversal, paths, neighborhood)
- ✅ Búsqueda semántica (scoring, filtering, related nodes)
- ✅ Predicción de enlaces (missing links, suggestions)
- ✅ Análisis del grafo (importance, communities, metrics)
- ✅ Compatibilidad con MCP original

**Resultados:** 13/17 tests pasando (76% success rate)

## 📚 Casos de Uso

### 1. Exploración de Conocimiento
```python
# Un agente quiere entender la arquitectura del proyecto
mcp = get_advanced_mcp_server()

# Buscar conceptos relacionados
results = mcp.semantic_search("architecture", limit=5)

# Explorar vecindario de cada concepto
for result in results:
    neighborhood = mcp.get_node_neighborhood(result['id'], radius=1)
    print(f"Concepto: {result['id']}")
    print(f"Conectado a: {len(neighborhood['nodes'])} nodos")
```

### 2. Validación de Coherencia
```python
# Encontrar nodos aislados o mal conectados
metrics = mcp.get_graph_metrics()
importance = mcp.analyze_node_importance()

# Nodos con baja importancia pueden necesitar más conexiones
low_importance = [n for n in importance if n['importance_score'] < 10]

for node in low_importance:
    suggestions = mcp.suggest_new_links(node['id'], max_suggestions=3)
    print(f"{node['id']} podría conectarse con:")
    for sugg in suggestions:
        print(f"  - {sugg['target']} (score: {sugg['score']:.3f})")
```

### 3. Descubrimiento de Patrones
```python
# Identificar comunidades de conocimiento
communities = mcp.detect_communities()

# Analizar cada comunidad
for comm_id, nodes in communities.items():
    print(f"\n{comm_id}:")
    
    # Encontrar el nodo más importante de la comunidad
    comm_importance = [n for n in importance if n['id'] in nodes]
    if comm_importance:
        leader = max(comm_importance, key=lambda x: x['importance_score'])
        print(f"  Nodo central: {leader['id']}")
```

### 4. Navegación Guiada
```python
# Encontrar el camino de aprendizaje entre dos conceptos
path = mcp.find_shortest_path("beginner_concept", "advanced_concept")

if path:
    print("Ruta de aprendizaje:")
    for i, node_id in enumerate(path):
        node = mcp.kg.get_node_data(node_id)
        print(f"{i+1}. {node_id}")
        print(f"   {node.content[:100]}...")
```

## 🎯 Beneficios para Agentes de IA

1. **Navegación Inteligente**: Los agentes pueden explorar el grafo de manera eficiente
2. **Búsqueda Contextual**: Encontrar información relevante con scoring semántico
3. **Descubrimiento Automático**: Predicción de enlaces sugiere conexiones faltantes
4. **Análisis Estructural**: Entender la topología y organización del conocimiento
5. **Validación de Coherencia**: Detectar gaps y oportunidades de mejora

## 🔄 Compatibilidad

El `AdvancedMCPServer` mantiene compatibilidad total con el `EnhancedMCPServer` original:

```python
# Métodos legacy siguen funcionando
mcp.get_node("node_id")
mcp.search_nodes("query", node_type="concept")
mcp.get_coding_standards()
mcp.export_for_agent("claude")
```

## 📈 Próximas Mejoras

- [ ] PageRank para ranking de nodos más sofisticado
- [ ] Algoritmos de clustering más avanzados (Louvain, Label Propagation)
- [ ] Embeddings de nodos para similitud semántica profunda
- [ ] Visualización interactiva del grafo (D3.js, Cytoscape)
- [ ] Cache de resultados para queries frecuentes
- [ ] Soporte para grafos temporales (evolución del conocimiento)

## 🎓 Conclusión

El MCP Server ahora ofrece capacidades de clase enterprise para interactuar con el grafo de conocimiento. Los agentes de IA pueden navegar, buscar, analizar y descubrir relaciones de manera sofisticada, maximizando el valor del grafo como fuente de verdad para el desarrollo del proyecto.
