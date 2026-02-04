# Waterfall Stage Tracking System

## 🎯 Overview

El sistema de tracking de cascada gestiona el progreso de features a través de las etapas de desarrollo, asegurando que no se salten pasos y manteniendo un registro completo del historial.

## 📋 Etapas de la Cascada

1. **ANALYSIS** - Definir requisitos y alcance
2. **DESIGN** - Arquitectura y especificaciones
3. **IMPLEMENTATION** - Codificación y tests unitarios
4. **TESTING** - Suite completa de tests
5. **DOCUMENTATION** - Docs y actualización del grafo
6. **RELEASE** - Versionado y despliegue
7. **COMPLETED** - Feature finalizado

## 🚀 Comandos CLI

### Iniciar tracking de una feature

```bash
uv run python3 -m ai_dev_graph.cli waterfall start FEATURE_ID "Feature Title"

# Ejemplo
uv run python3 -m ai_dev_graph.cli wf start auth_system "Authentication System"
```

### Ver estado actual

```bash
# Feature más reciente
uv run python3 -m ai_dev_graph.cli wf status

# Feature específica
uv run python3 -m ai_dev_graph.cli wf status --feature FEATURE_ID
```

### Avanzar a la siguiente etapa

```bash
uv run python3 -m ai_dev_graph.cli wf advance FEATURE_ID
```

**IMPORTANTE**: Solo se puede avanzar cuando la etapa actual esté completada.

### Retroceder a etapa anterior

```bash
# Con razón
uv run python3 -m ai_dev_graph.cli wf regress FEATURE_ID --reason "Tests failing"

# Sin razón específica
uv run python3 -m ai_dev_graph.cli wf regress FEATURE_ID
```

Usar cuando se encuentren problemas que requieren volver a una etapa previa.

### Añadir notas

```bash
uv run python3 -m ai_dev_graph.cli wf note FEATURE_ID "Checkpoint: completed API endpoints"
```

### Listar features

```bash
# Todas las features
uv run python3 -m ai_dev_graph.cli wf list

# Filtrar por etapa
uv run python3 -m ai_dev_graph.cli wf list --stage implementation
```

### Ver estadísticas

```bash
uv run python3 -m ai_dev_graph.cli wf stats
```

## 🔄 Flujo de Trabajo Típico

```bash
# 1. Iniciar feature
uv run python3 -m ai_dev_graph.cli wf start new_api "New API Endpoint"

# 2. Completar análisis
# ... trabajar en análisis ...
uv run python3 -m ai_dev_graph.cli wf advance new_api

# 3. Completar diseño
# ... diseñar arquitectura ...
uv run python3 -m ai_dev_graph.cli wf advance new_api

# 4. Implementar
# ... escribir código ...
uv run python3 -m ai_dev_graph.cli wf advance new_api

# 5. Testing
# ... ejecutar tests ...
uv run python3 -m ai_dev_graph.cli wf advance new_api

# 6. Documentación
# ... actualizar docs ...
uv run python3 -m ai_dev_graph.cli wf advance new_api

# 7. Release
# ... bump version ...
uv run python3 -m ai_dev_graph.cli wf advance new_api

# Feature COMPLETED
```

## 📊 Persistencia

El estado se guarda en: `data/waterfall_state.json`

Formato:
```json
{
  "feature_id": {
    "feature_id": "db_persistence",
    "title": "Database Implementation",
    "current_stage": "testing",
    "started_at": "2026-02-04T20:00:00",
    "updated_at": "2026-02-04T21:30:00",
    "stage_history": [
      {
        "stage": "analysis",
        "completed_at": "2026-02-04T20:15:00"
      },
      {
        "stage": "design",
        "completed_at": "2026-02-04T20:45:00"
      }
    ],
    "notes": "Checkpoint notes here"
  }
}
```

## 📝 Nodos en el Grafo

El sistema añade los siguientes nodos al grafo de conocimiento:

- **waterfall_methodology** - Concepto principal
- **stage_analysis** - Regla de análisis
- **stage_design** - Regla de diseño
- **stage_implementation** - Regla de implementación
- **stage_testing** - Regla de testing
- **stage_documentation** - Regla de documentación
- **stage_release** - Regla de release
- **rule_no_skip_stages** - Prohibición de saltar etapas
- **instruction_track_progress** - Instrucción de tracking

Consultar con:
```bash
uv run python3 -m ai_dev_graph.cli stats
```

## ⚠️ Reglas Importantes

1. **No Saltar Etapas**: Cada etapa debe completarse antes de avanzar
2. **Retroceder si Necesario**: Si hay problemas, retroceder a la etapa apropiada
3. **Documentar Progreso**: Usar notas para checkpoints importantes
4. **Consultar Estado**: Antes de empezar, verificar en qué etapa está la feature

## 🎯 Beneficios

- ✅ **No Perder el Hilo**: Siempre sabes en qué etapa estás
- ✅ **Historial Completo**: Registro de cuándo se completó cada etapa
- ✅ **Flujo Disciplinado**: Obliga a seguir el proceso cascada
- ✅ **Múltiples Features**: Trackear varias features en paralelo
- ✅ **Notas Contextuales**: Añadir información importante en cada etapa

## 📖 Ejemplos de Uso

### Ejemplo 1: Feature Nueva

```bash
# Iniciar
uv run python3 -m ai_dev_graph.cli wf start user_profile "User Profile Management"

# Trabajar en análisis
uv run python3 -m ai_dev_graph.cli wf note user_profile "Requirements: CRUD for user profiles"
uv run python3 -m ai_dev_graph.cli wf advance user_profile

# Diseño
uv run python3 -m ai_dev_graph.cli wf note user_profile "Using Pydantic models + FastAPI"
uv run python3 -m ai_dev_graph.cli wf advance user_profile

# ... continuar ...
```

### Ejemplo 2: Encontrar Bug en Testing

```bash
# Estamos en testing
uv run python3 -m ai_dev_graph.cli wf status

# Encontramos bug en implementación
uv run python3 -m ai_dev_graph.cli wf regress feature_id --reason "Bug in validation logic"

# Volver a implementation, arreglar, y re-avanzar
```

### Ejemplo 3: Múltiples Features

```bash
# Feature 1
uv run python3 -m ai_dev_graph.cli wf start api_v2 "API Version 2"

# Feature 2
uv run python3 -m ai_dev_graph.cli wf start cache_layer "Redis Cache Layer"

# Ver todas
uv run python3 -m ai_dev_graph.cli wf list

# Ver solo las en implementation
uv run python3 -m ai_dev_graph.cli wf list --stage implementation
```

## 🔧 Integración con Git

Recomendado: hacer commit al completar cada etapa

```bash
# Completar etapa
uv run python3 -m ai_dev_graph.cli wf advance my_feature

# Commit con mensaje descriptivo
git add .
git commit -m "feat(my_feature): completed design stage"
```

---

**El tracking de cascada asegura un desarrollo disciplinado y sin perder el contexto** 🚀
