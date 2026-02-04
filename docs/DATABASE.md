# Database Persistence Layer

## Overview

AI Dev Graph now uses a **SQLite database** for persistent graph storage, providing ACID guarantees and better performance while maintaining simplicity.

## Architecture

### Hybrid Approach

- **NetworkX**: In-memory graph engine for fast operations and graph algorithms
- **SQLite**: Persistent storage with transactional integrity
- **Dual-layer design**: All graph modifications are automatically synced to both layers

### Benefits

1. **ACID Compliance**: Atomic, Consistent, Isolated, Durable operations
2. **No External Dependencies**: SQLite is embedded, no server required
3. **Better Performance**: Indexed queries for fast node/edge lookups
4. **Incremental Updates**: No need to reload entire graph on changes
5. **Backup-Friendly**: Single file database, easy to backup/restore

## Database Schema

### Nodes Table
```sql
CREATE TABLE nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Edges Table
```sql
CREATE TABLE edges (
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source, target),
    FOREIGN KEY (source) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target) REFERENCES nodes(id) ON DELETE CASCADE
)
```

## Migration from JSON

The system automatically migrates existing JSON graphs to the database on first run:

```bash
# The migration happens automatically when you load the graph
uv run python3 -m ai_dev_graph.cli init
```

If `graphs/v0_initial.json` exists and the database is empty, the graph will be:
1. Loaded from JSON
2. Migrated to SQLite database at `data/graph.db`
3. Ready for use

## CLI Commands

### Database Information
```bash
uv run python3 -m ai_dev_graph.cli db info
```

Shows database stats, file size, node count, and type distribution.

### Backup Database
```bash
uv run python3 -m ai_dev_graph.cli db backup
```

Creates timestamped backup in `data/backups/`.

### Export to JSON
```bash
uv run python3 -m ai_dev_graph.cli db export --output graphs/backup.json
```

Exports database to JSON format (useful for version control).

### Import from JSON
```bash
# Import and merge
uv run python3 -m ai_dev_graph.cli db import graphs/v0_initial.json

# Import and replace
uv run python3 -m ai_dev_graph.cli db import graphs/v0_initial.json --clear
```

## File Locations

- **Database**: `data/graph.db`
- **Backups**: `data/backups/graph_backup_YYYYMMDD_HHMMSS.db`
- **JSON Exports**: `graphs/` (configurable)

## Node Quality Rule

A new rule has been added to the graph:

**rule_node_quality**: "Solo añadir nodos que aporten valor real al grafo. Evitar nodos redundantes o temporales de testing. Cada nodo debe documentar conocimiento persistente y relevante."

This enforces that only meaningful, persistent knowledge is stored.

## Best Practices

1. **Regular Backups**: Use `db backup` before major changes
2. **Version Control**: Export to JSON periodically for git tracking
3. **Quality Over Quantity**: Follow the node quality rule
4. **Monitor Size**: Check `db info` to monitor graph growth

## Performance Notes

- SQLite handles millions of nodes efficiently
- Indexes on `type`, `source`, and `target` ensure fast queries
- In-memory NetworkX provides O(1) graph traversal
- Combined approach gives best of both worlds

## Backward Compatibility

- JSON save/load methods still available
- Can disable database with `use_db=False` parameter
- Legacy JSON files are auto-migrated seamlessly
