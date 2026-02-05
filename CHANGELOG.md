## v0.4.0 (2026-02-05)

### Feat

#### Neo4j Integration and Persistence Abstraction

- **Neo4j Support**: Added support for Neo4j as the primary graph database.
- **Persistence Abstraction**: Introduced `GraphRepository` and `PersistenceFactory` to support multiple backends.
- **Configuration**: Switch between Neo4j (default) and SQLite via `DATABASE_TYPE` environment variable.
- **Semantic Mapping**: Nodes are stored with semantic labels in Neo4j.

## v0.3.0 (2026-02-05)

### Feat

#### Enhanced MCP Server with AI Agent Assistance

- **Complete rewrite** of MCP server with advanced capabilities
- **Waterfall integration**: Get current feature stage and guidance from knowledge graph
- **Rule validation**: Validate actions against graph rules before execution
- **Context-aware suggestions**: Get prioritized next actions based on current stage
- **Enhanced search**: Relevance scoring and relationship tracking
- **Optimized export**: Complete development context for AI agents

**New CLI Commands** (`agent` / `ai`):
- `context` - Get development context with stage guidance
- `suggest` - Get prioritized next actions
- `validate` - Validate actions against graph rules
- `standards` - Get all coding standards from graph
- `export` - Export optimized context for AI agents

**Documentation**: Complete guide in `docs/ENHANCED_MCP.md`

#### Waterfall Stage Tracking System

- **Stage management**: Track features through waterfall stages (ANALYSIS → DESIGN → IMPLEMENTATION → TESTING → DOCUMENTATION → RELEASE → COMPLETED)
- **Knowledge graph integration**: 9 nodes added defining waterfall methodology
- **Progress tracking**: Persistent state in `data/waterfall_state.json`
- **Stage enforcement**: Prevents skipping stages with rule validation
- **History tracking**: Complete log of stage completions

**New CLI Commands** (`waterfall` / `wf`):
- `start` - Start tracking new feature
- `status` - Show current feature status
- `advance` - Move to next stage
- `regress` - Go back to previous stage
- `note` - Add notes to feature
- `list` - List all features
- `stats` - Show statistics

**Documentation**: Complete guide in `docs/WATERFALL_TRACKING.md`

#### Activity Logs Audit

- **E2E tests** for activity logs functionality (Playwright)
- **Browser automation** audit completed with validation
- **Audit report** generated in `LOGS_AUDIT_REPORT.md`

### Improvements

- Enhanced documentation structure
- README updated with new features
- Complete usage examples and best practices

## v0.2.0 (2026-02-04)

### BREAKING CHANGE

- Graph storage migrated from JSON-only to SQLite database

### Feat

- initial implementation with database persistence
