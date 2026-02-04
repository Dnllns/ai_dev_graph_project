# Git Repository - Reinitializado

## ✅ Estado del Repositorio

El repositorio ha sido **reinicializado exitosamente** con:

- ✅ Nuevo repositorio Git (rama `main`)
- ✅ Commitizen configurado para conventional commits
- ✅ Changelog automático generado
- ✅ Versión bumpeada a **v0.2.0**
- ✅ Tag creado: `v0.2.0`
- ✅ `.gitignore` configurado

## 📋 Commits Actuales

```
54f1650 (HEAD -> main, tag: v0.2.0) bump: version 0.1.0 → 0.2.0
64b92f9 feat: initial implementation with database persistence
```

## 📝 CHANGELOG.md

```markdown
## v0.2.0 (2026-02-04)

### BREAKING CHANGE

- Graph storage migrated from JSON-only to SQLite database

### Feat

- initial implementation with database persistence
```

## 🔧 Commitizen Configurado

El proyecto usa **Commitizen** para commits convencionales:

### Hacer un commit nuevo

```bash
# Opción 1: Interactivo con commitizen
uv run cz commit

# Opción 2: Manual con conventional commits
git commit -m "feat: nueva funcionalidad"
git commit -m "fix: corrección de bug"
git commit -m "docs: actualización de documentación"
```

### Tipos de commits disponibles

- **feat**: Nueva funcionalidad
- **fix**: Corrección de bugs
- **docs**: Cambios en documentación
- **style**: Cambios de formato (no afectan código)
- **refactor**: Refactorización de código
- **perf**: Mejoras de performance
- **test**: Añadir o modificar tests
- **chore**: Tareas de mantenimiento

### Generar changelog

```bash
# Bump versión y actualizar changelog
uv run cz bump --changelog

# Solo generar changelog
uv run cz changelog
```

## 📦 Versión Actual

**v0.2.0** (2026-02-04)

La versión se gestiona automáticamente en:
- `pyproject.toml` (campo `version`)
- Git tags
- `CHANGELOG.md`

## 🎯 Próximos Pasos

Para seguir trabajando con el repositorio:

1. **Hacer cambios al código**
2. **Stage los cambios**: `git add .`
3. **Commit con commitizen**: `uv run cz commit`
4. **Bump versión**: `uv run cz bump --changelog`

## 📚 Configuración de Commitizen

La configuración está en `pyproject.toml`:

```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.2.0"
version_scheme = "semver"
version_provider = "pep621"
update_changelog_on_bump = true
tag_format = "v$version"
```

## ✨ Beneficios

- **Changelog automático**: Se genera desde los commits
- **Versionado semántico**: Automático basado en commits
- **Commits estandarizados**: Fácil de entender el historial
- **CI/CD ready**: Compatible con pipelines automáticas

---

**Repositorio listo para desarrollo** 🚀
