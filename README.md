# AI Dev Graph

Motor de conocimiento estructurado para agentes de IA. Almacena objetivos e instrucciones en grafos para eliminar ambigüedad en el proceso de desarrollo.

## 🎯 Filosofía
**GRAFO · PYTHON · API · DOC · TEST**

## 🧠 El Grafo es la Clave
El conocimiento no es texto plano; es una red de dependencias.
- **Nodos:** Requisitos, arquitecturas, estándares, guías de estilo, decisiones técnicas.
- **Aristas:** Relaciones semánticas (depende de, implementa, valida).
- **Propósito:** Proporcionar al agente (Claude Code, Copilot) el contexto exacto necesario sin ruido.

## 🛠️ Stack y Gestión
- **Lenguaje:** Python 3.11+
- **Grafos:** NetworkX para topología de dependencias
- **API:** FastAPI con interfaz REST completa
- **Interfaz:** Admin panel web interactivo moderno
- **Persistencia:** SQLite + NetworkX (híbrido) con ACID guarantees
- **Backups:** Automáticos con timestamp
- **CLI:** Herramientas de línea de comandos para todas las operaciones

## ✨ Características

### 🚀 API REST Completa
- CRUD de nodos con validación
- Búsqueda y filtrado avanzado
- Contexto relacional (padres/hijos)
- Estadísticas en tiempo real
- Exportación optimizada para agentes

### 📊 Interfaz de Administración
- Dashboard con estadísticas
- Gestión interactiva de nodos
- Búsqueda en vivo
- Visualización de contexto
- Descarga de datos

### 🔧 CLI Intuitivo
```bash
# Servidor
python -m ai_dev_graph.cli server          # Iniciar servidor

# Gestión de grafo
python -m ai_dev_graph.cli init            # Inicializar grafo
python -m ai_dev_graph.cli stats           # Ver estadísticas
python -m ai_dev_graph.cli validate        # Validar integridad
python -m ai_dev_graph.cli export          # Exportar para agentes

# Base de datos
python -m ai_dev_graph.cli db info         # Info de la BD
python -m ai_dev_graph.cli db backup       # Backup de BD
python -m ai_dev_graph.cli db export       # Exportar a JSON
python -m ai_dev_graph.cli db import FILE  # Importar desde JSON

# Waterfall tracking
python -m ai_dev_graph.cli wf start ID "Title"  # Iniciar feature
python -m ai_dev_graph.cli wf status            # Ver estado
python -m ai_dev_graph.cli wf advance ID        # Avanzar etapa
python -m ai_dev_graph.cli wf list              # Listar features
```

### 📦 GraphManager Avanzado
- Carga/creación automática
- Backups con timestamp
- Validación de integridad
- Recomendaciones inteligentes
- Exportación para diferentes agentes

## 🚀 Inicio Rápido

### 1. Instalar

```bash
pip install -e .
```

### 2. Iniciar Servidor

```bash
python -m ai_dev_graph.cli server
```

### 3. Acceder

- **Admin:** http://localhost:8000/admin
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

### 4. Crear Primer Nodo

A través del panel de administración o via API:

```bash
curl -X POST http://localhost:8000/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "id": "mi_concepto",
    "type": "concept",
    "content": "Mi primer concepto",
    "parents": []
  }'
```

## 🌊 Metodología de Cascada

El proyecto implementa un **flujo de desarrollo en cascada con implementación continua**:

1. **ANALYSIS** → 2. **DESIGN** → 3. **IMPLEMENTATION** → 4. **TESTING** → 5. **DOCUMENTATION** → 6. **RELEASE** → 7. **COMPLETED**

### Tracking de Progreso

```bash
# Iniciar feature
python -m ai_dev_graph.cli wf start my_feature "Description"

# Avanzar etapa
python -m ai_dev_graph.cli wf advance my_feature
```

**Regla**: No saltar etapas. Ver [docs/WATERFALL_TRACKING.md](docs/WATERFALL_TRACKING.md)

## 📖 Documentación

- [Guía Completa](docs/USAGE.md) - Tutorial completo y ejemplos
- [Waterfall Tracking](docs/WATERFALL_TRACKING.md) - Sistema de gestión de etapas
- [Database](docs/DATABASE.md) - Persistencia con SQLite
- [API Reference](docs/index.md) - Documentación técnica
- [Tests](tests/) - Ejemplos de uso

## 🏗️ Arquitectura

```
KnowledgeGraph
├── Nodos (7 tipos)
├── Aristas (relaciones)
└── Operaciones
    ├── Consulta (get_context)
    ├── Búsqueda (find_nodes)
    ├── Actualización (update_node)
    └── Eliminación (delete_node)

GraphManager
├── Persistencia
├── Versionado
├── Validación
└── Exportación

API REST (FastAPI)
├── CRUD de nodos
├── Estadísticas
├── Búsqueda
└── Exportación

Admin Web (HTML/JS)
├── Dashboard
├── Gestión
├── Búsqueda
└── Configuración
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=ai_dev_graph

# Modo verbose
pytest -v
```

## 🤖 Uso para Agentes

El agente consulta el grafo para:
1. Comprender requisitos y restricciones
2. Conocer estándares de código
3. Descubrir dependencias entre componentes
4. Acceder a decisiones técnicas documentadas
5. Validar cambios contra las reglas

Ejemplo:

```python
import requests

# Obtener estándares de código
response = requests.get(
    "http://localhost:8000/nodes",
    params={"type": "rule", "content_match": "style"}
)
standards = response.json()

# Aplicar conocimiento en desarrollo...
```

## 📋 Tipos de Nodos

- **project** - Nodo raíz del proyecto
- **concept** - Ideas abstractas y filosofías
- **rule** - Requisitos obligatorios
- **guideline** - Recomendaciones
- **instruction** - Tareas específicas
- **resource** - Archivos y herramientas
- **test** - Criterios de validación

## 🔄 Flujo de Trabajo

1. **Inicializar** → `cli init`
2. **Desarrollar** → UI web o API
3. **Validar** → `cli validate`
4. **Exportar** → `cli export --agent claude`
5. **Integrar** → Usar en agentes

## 📦 Dependencias

- `networkx>=3.2.1` - Grafos
- `fastapi>=0.109.0` - API
- `uvicorn>=0.27.0` - Servidor ASGI
- `pydantic>=2.6.0` - Validación de datos

### Dev

- `pytest>=8.0.0` - Testing
- `ruff>=0.1.0` - Linting
- `commitizen>=3.15.0` - Versionado

## 🤝 Contribuir

1. Fork el proyecto
2. Crea rama para tu feature
3. Commit y push
4. Abre PR

## 📄 Licencia

MIT

## 🔗 Referencias

- [NetworkX](https://networkx.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
