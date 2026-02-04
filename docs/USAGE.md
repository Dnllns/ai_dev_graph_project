# AI Dev Graph - Guía Completa

## 📋 Índice

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Uso Rápido](#uso-rápido)
4. [Interfaz de Administración](#interfaz-de-administración)
5. [API REST](#api-rest)
6. [CLI](#cli)
7. [Desarrollo](#desarrollo)

---

## Introducción

**AI Dev Graph** es un motor de conocimiento estructurado para agentes de IA que almacena objetivos e instrucciones en grafos para eliminar ambigüedad en el proceso de desarrollo.

### 🎯 Filosofía

```
GRAFO · PYTHON · API · DOC · TEST
```

- **Nodos:** Requisitos, arquitecturas, estándares, guías de estilo, decisiones técnicas
- **Aristas:** Relaciones semánticas (depende de, implementa, valida)
- **Propósito:** Proporcionar al agente el contexto exacto necesario sin ruido

---

## Instalación

### Requisitos

- Python 3.11+
- pip o uv

### Instalación Local

```bash
# Clonar el proyecto
git clone <repo>
cd ai_dev_graph_project

# Instalar en modo desarrollo
pip install -e .

# O con uv
uv pip install -e .
```

### Instalar Dependencias Opcionales

```bash
# Para desarrollo y testing
pip install -e ".[dev]"

# O con uv
uv pip install -e ".[dev]"
```

---

## Uso Rápido

### 1. Iniciar el Servidor

```bash
python -m ai_dev_graph.cli server
```

El servidor estará disponible en:
- **Admin Panel:** http://localhost:8000/admin
- **API Docs:** http://localhost:8000/docs
- **API Base:** http://localhost:8000

### 2. Acceder a la Interfaz de Administración

Abre tu navegador en `http://localhost:8000/admin` para acceder al panel completo de administración.

### 3. Crear tu Primer Nodo

A través de la interfaz:
1. Ve a "➕ Crear Nodo"
2. Completa el formulario:
   - ID: `mi_primer_concepto`
   - Tipo: `Concepto`
   - Contenido: `Mi primer conocimiento`
3. Haz clic en "✓ Crear Nodo"

---

## Interfaz de Administración

### 📊 Dashboard

Visualiza estadísticas en tiempo real:
- Total de nodos
- Número de conexiones
- Densidad del grafo
- Desglose por tipo de nodo

### 📌 Gestión de Nodos

- **Listar:** Visualiza todos los nodos con búsqueda en vivo
- **Ver:** Consulta detalles completos y contexto de un nodo
- **Crear:** Añade nuevos nodos con relaciones
- **Eliminar:** Elimina nodos del grafo

### 🔍 Búsqueda Avanzada

Busca nodos por:
- Tipo (Proyecto, Concepto, Regla, etc.)
- Contenido (búsqueda parcial)

### ⚙️ Configuración

Operaciones globales:
- **Guardar:** Persistir cambios del grafo
- **Descargar:** Exportar grafo como JSON
- **Reiniciar:** Restaurar configuración inicial

---

## API REST

### Endpoints Principales

#### Health Check

```http
GET /health
```

Respuesta:
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

#### Obtener Grafo Completo

```http
GET /graph
```

Retorna la estructura completa del grafo en formato NetworkX.

#### Estadísticas

```http
GET /graph/stats
```

Retorna:
```json
{
  "total_nodes": 10,
  "total_edges": 15,
  "density": 0.167,
  "node_types": {
    "project": 1,
    "concept": 5,
    "rule": 4
  }
}
```

#### Estadísticas Avanzadas

```http
GET /graph/advanced-stats
```

Incluye recomendaciones y métricas adicionales.

#### Listar Nodos

```http
GET /nodes?type=concept&content_match=python
```

Parámetros:
- `type` (opcional): Filtrar por tipo
- `content_match` (opcional): Buscar en contenido

#### Obtener Nodo Específico

```http
GET /nodes/{node_id}?depth=2
```

Parámetros:
- `depth`: Profundidad de contexto (1-3)

#### Crear Nodo

```http
POST /nodes
Content-Type: application/json

{
  "id": "mi_nodo",
  "type": "concept",
  "content": "Descripción del concepto",
  "metadata": {"clave": "valor"},
  "parents": ["nodo_padre1", "nodo_padre2"]
}
```

#### Actualizar Nodo

```http
PUT /nodes/{node_id}
Content-Type: application/json

{
  "content": "Nuevo contenido",
  "metadata": {"nueva_clave": "nuevo_valor"}
}
```

#### Eliminar Nodo

```http
DELETE /nodes/{node_id}
```

#### Validar Grafo

```http
GET /graph/validate
```

Retorna reporte de integridad.

#### Exportar para Agente

```http
GET /graph/export?agent_type=claude
```

Exporta el grafo optimizado para consumo de agentes.

#### Guardar Grafo

```http
POST /graph/save
```

#### Reiniciar Grafo

```http
POST /graph/reset
```

---

## CLI

### Inicializar Grafo

```bash
python -m ai_dev_graph.cli init
```

### Mostrar Estadísticas

```bash
python -m ai_dev_graph.cli stats
```

Salida:
```
📈 GRAPH STATISTICS
==================================================
Total Nodes: 5
Total Edges: 8
Density: 0.4000
Average Degree: 3.2
...
```

### Validar Grafo

```bash
python -m ai_dev_graph.cli validate
```

### Exportar Grafo

```bash
# Para Claude
python -m ai_dev_graph.cli export --agent claude --output export.json

# Para otros agentes
python -m ai_dev_graph.cli export --agent default --output export.json
```

### Iniciar Servidor

```bash
# En puerto por defecto (8000)
python -m ai_dev_graph.cli server

# Con puerto personalizado
python -m ai_dev_graph.cli server --port 8080

# Con auto-reload (desarrollo)
python -m ai_dev_graph.cli server --reload

# En host específico
python -m ai_dev_graph.cli server --host 127.0.0.1 --port 8000
```

---

## Desarrollo

### Estructura del Proyecto

```
ai_dev_graph/
├── core/
│   ├── graph.py              # Core graph engine
│   └── __init__.py
├── api/
│   ├── main.py               # FastAPI application
│   ├── static/
│   │   └── index.html        # Admin interface
│   └── __init__.py
├── models/
│   ├── manager.py            # High-level graph management
│   └── __init__.py
├── init_meta_graph.py        # Graph initialization
├── update_*.py               # Update utilities
├── cli.py                    # CLI interface
└── __init__.py
```

### Tipos de Nodos

```python
class NodeType(str, Enum):
    PROJECT = "project"           # Nodo raíz
    CONCEPT = "concept"           # Ideas abstractas
    RULE = "rule"                 # Obligatorio
    GUIDELINE = "guideline"       # Recomendado
    INSTRUCTION = "instruction"   # Tarea específica
    RESOURCE = "resource"         # Archivos, herramientas
    TEST = "test"                 # Criterios de validación
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con verbosidad
pytest -v

# Un archivo específico
pytest tests/test_core.py

# Con cobertura
pytest --cov=ai_dev_graph
```

### Tests E2E con Playwright

Los tests E2E prueban la interfaz web completa con Playwright.

#### Instalación

```bash
# Instalar Playwright y dependencias
pip install playwright>=1.40.0 pytest-asyncio>=0.23.0

# Descargar navegadores (requerido una sola vez)
playwright install
```

#### Ejecutar Tests E2E

```bash
# Todos los tests E2E
pytest tests/test_e2e.py -v

# Tests específicos
pytest tests/test_e2e.py::TestAdminDashboard -v

# Con navegador visible (headful)
pytest tests/test_e2e.py -v --headed

# En diferentes navegadores
pytest tests/test_e2e.py -v --browser chromium
pytest tests/test_e2e.py -v --browser firefox
pytest tests/test_e2e.py -v --browser webkit

# Solo tests unitarios (excluir E2E)
pytest -m "not asyncio"
```

#### Cobertura de Tests E2E

**Dashboard Tests:**
- Carga del panel admin
- Visualización de estadísticas
- Navegación entre secciones

**Crear Nodos:**
- Formulario visible y funcional
- Crear nodos simples
- Crear con metadatos

**Gestión de Nodos:**
- Listar nodos
- Búsqueda en vivo
- Ver detalles en modal

**Búsqueda Avanzada:**
- Buscar por tipo
- Buscar por contenido

**Configuración:**
- Página de configuración
- Descargar grafo como JSON

**Responsividad:**
- Vista móvil (375x667)
- Vista tablet (768x1024)

**Flujos Completos:**
- Crear y buscar nodo
- Crear, ver y listar nodos

**Integración API:**
- Health check
- Endpoints de grafo
- Crear nodo vía API y verificar en UI

**Elementos UI:**
- Botón de actualización
- Reset de formularios
- Cierre de modales

#### Debugging Tests E2E

```python
# Agregar pausa en test
await page.pause()

# Screenshot
await page.screenshot(path="screenshot.png")

# Grabar video
pytest tests/test_e2e.py --record-video=on

# Inspector de Playwright
pytest tests/test_e2e.py --inspector

# Ver logs detallados
pytest tests/test_e2e.py -v -s
```

#### Mejores Prácticas

```python
# Usar selectores confiables
await page.click('button:has-text("Crear")')

# Esperar elementos correctamente
await page.wait_for_selector("#nodeId", timeout=5000)

# Usar context managers para navegación
async with page.expect_navigation():
    await page.click("a")

# Tiempos de espera apropiados
await page.wait_for_selector(".alert-success", timeout=5000)
```

---

```python
from ai_dev_graph.core.graph import KnowledgeGraph, NodeData, NodeType

# Crear grafo
kg = KnowledgeGraph()

# Añadir nodos
root = NodeData(
    id="proyecto",
    type=NodeType.PROJECT,
    content="Mi proyecto"
)
kg.add_knowledge(root)

# Añadir nodos relacionados
feature = NodeData(
    id="feature_x",
    type=NodeType.CONCEPT,
    content="Feature X"
)
kg.add_knowledge(feature, parents=["proyecto"])

# Consultar contexto
context = kg.get_context("proyecto")
print(f"Hijos: {context['children']}")

# Buscar nodos
concepts = kg.find_nodes(type=NodeType.CONCEPT)

# Guardar
kg.save("mi_grafo.json")
```

### Usar GraphManager

```python
from ai_dev_graph.models.manager import get_graph_manager

manager = get_graph_manager()

# Cargar o crear
kg = manager.load_or_create()

# Guardar con backup automático
manager.save_with_backup()

# Validar
report = manager.validate_graph()

# Exportar para agente
export = manager.export_for_agent("claude")

# Obtener recomendaciones
recommendations = manager.get_recommendations()
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Mensaje de información")
logger.warning("Advertencia")
logger.error("Error")
```

---

## Flujo de Trabajo Típico

### 1. Inicialización

```bash
python -m ai_dev_graph.cli init
```

### 2. Desarrollo

Accede a `http://localhost:8000/admin` y comienza a crear nodos.

### 3. Validación

```bash
python -m ai_dev_graph.cli validate
```

### 4. Exportación

```bash
python -m ai_dev_graph.cli export --agent claude
```

### 5. Integración

Usa la API REST para consultar el grafo desde tus agentes:

```python
import requests

# Obtener estadísticas
response = requests.get("http://localhost:8000/graph/stats")
stats = response.json()

# Buscar nodos específicos
response = requests.get("http://localhost:8000/nodes", 
                       params={"type": "rule"})
rules = response.json()

# Obtener contexto de un nodo
response = requests.get(f"http://localhost:8000/nodes/proyecto?depth=2")
context = response.json()
```

---

## Troubleshooting

### El servidor no inicia

```bash
# Verificar puerto en uso
lsof -i :8000

# Usar puerto diferente
python -m ai_dev_graph.cli server --port 8080
```

### Errores de importación

```bash
# Reinstalar en modo desarrollo
pip install -e .

# O verificar instalación
python -c "import ai_dev_graph; print(ai_dev_graph.__version__)"
```

### Tests fallan

```bash
# Ejecutar con más detalle
pytest -vv --tb=short

# Limpiar caché
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push y abre un PR

---

## Licencia

Ver [LICENSE](LICENSE)

---

## Recursos

- [NetworkX Documentation](https://networkx.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
