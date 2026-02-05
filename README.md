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

# Enhanced MCP - AI Agent Assistance
python -m ai_dev_graph.cli agent context       # Get dev context
python -m ai_dev_graph.cli agent suggest       # Get suggestions
python -m ai_dev_graph.cli agent validate "action"  # Validate action
python -m ai_dev_graph.cli agent standards     #  Get coding standards
python -m ai_dev_graph.cli agent export        # Export for AI
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

## 🤖 Enhanced MCP - AI Agent Assistance

El servidor MCP mejorado proporciona asistencia inteligente para desarrollo:

```bash
# Obtener contexto de desarrollo
python -m ai_dev_graph.cli agent context

# Ver acciones sugeridas basadas en etapa actual
python -m ai_dev_graph.cli agent suggest

# Validar acción contra reglas del grafo
python -m ai_dev_graph.cli agent validate "skip testing"

# Obtener estándares de código
python -m ai_dev_graph.cli agent standards

# Exportar contexto completo para AI
python -m ai_dev_graph.cli agent export --type claude
```

**Features**:
- 🎯 Contexto consciente de etapa waterfall
- ✅ Validación contra reglas del grafo
- 💡 Sugerencias priorizadas de próximas acciones
- 📐 Acceso a estándares y metodología
- 📤 Export optimizado para agentes AI

Ver: [docs/ENHANCED_MCP.md](docs/ENHANCED_MCP.md)

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

## 💾 Configuración de Persistencia

El sistema soporta por defecto **Neo4j**, pero puede usar **SQLite** como fallback.

Configuración (Environment Variables):
- `DATABASE_TYPE`: `neo4j` (default) o `sqlite`
- `NEO4J_URI`: URI de conexión (ej. `bolt://localhost:7687`)
- `NEO4J_USER`: Usuario (ej. `neo4j`)
- `NEO4J_PASSWORD`: Contraseña

## 📦 Dependencias

- `networkx>=3.2.1` - Grafos
- `fastapi>=0.109.0` - API
- `uvicorn>=0.27.0` - Servidor ASGI
- `pydantic>=2.6.0` - Validación de datos

### Dev

- `pytest>=8.0.0` - Testing
- `ruff>=0.1.0` - Linting
- `commitizen>=3.15.0` - Versionado

# 🚀 Ejecución de Pipelines Localmente con `act`

Este proyecto utiliza **GitHub Actions** para la Integración Continua (CI). Para ahorrar tiempo y evitar commits innecesarios, utilizamos [`act`](https://github.com/nektos/act) para correr los flujos de trabajo localmente.

## 🛠 Requisitos Previos

Antes de empezar, asegúrate de tener instalado:
1. **Docker**: `act` levanta contenedores para simular los runners de GitHub.
2. **Git**: Para la gestión del repositorio.

---

## 📥 Instalación de `act`

Dependiendo de tu sistema operativo, elige uno de los siguientes comandos:

### En macOS (Homebrew)
```bash
brew install nektos/tap/act
```

### En Linux (Script de instalación)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo sh
```

### En Windows (Chocolatey o Winget)

```bash
choco install act-cli
# O mediante winget
winget install nektos.act
```

---

## 🚀 Cómo usarlo

Una vez instalado, navega a la raíz del proyecto (donde está la carpeta `.github/`) y utiliza estos comandos:

### 1. Listar todas las acciones disponibles

```bash
act -l
```

### 2. Ejecutar la pipeline completa (Simular un Push)

```bash
act
```

### 3. Ejecutar un Job específico

Si tu archivo `.yml` tiene varios jobs (ej: `lint`, `test`, `docs`), puedes correr solo uno:

```bash
act -j test
```

### 4. Simular un evento específico (ej: Pull Request)

```bash
act pull_request
```

---

## ⚠️ Notas Importantes

* **Primera ejecución:** La primera vez que corras `act`, te preguntará qué "imagen" de Docker deseas usar (Small, Medium, Large). La opción **Medium** suele ser suficiente para la mayoría de proyectos de Python.
* **Variables de Entorno:** Si tu pipeline usa secretos (`secrets.GITHUB_TOKEN`, etc.), puedes crear un archivo `.secrets` localmente y ejecutar:
```bash
act --secret-file .secrets
```

* **Arquitectura:** Asegúrate de que Docker esté corriendo antes de lanzar el comando, de lo contrario, `act` fallará al no poder conectar con el demonio de Docker.

---

### Un tip de pro:
Si notas que `act` tarda mucho en descargar las imágenes de Docker cada vez, puedes usar el flag `--reuse` para que no borre los contenedores después de cada ejecución exitosa, acelerando el proceso de feedback.

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
