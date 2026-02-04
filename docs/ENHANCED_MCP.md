# Enhanced MCP Server - Usage Guide

## 🚀 Overview

The Enhanced MCP (Model Context Protocol) Server provides AI agents with intelligent access to the knowledge graph, waterfall tracking, and development assistance features.

## ✨ New Features

### 1. **Waterfall Integration**
- Query current feature stage
- Get stage-specific guidance
- Validate progression through stages

### 2. **Rule Validation**
- Validate actions against graph rules
- Detect rule violations before execution
- Get applicable rules for tasks

### 3. **Context-Aware Suggestions**
- Get next recommended actions
- Stage-specific recommendations
- Priority-based action lists

### 4. **Enhanced Search**
- Relevance scoring
- Type filtering
- Parent/child relationship included

### 5. **Agent Export**
- Optimized context for AI agents
- Includes methodology, standards, and current state
- Customizable for different agent types

## 📋 CLI Commands

### Get Development Context

```bash
uv run python3 -m ai_dev_graph.cli agent context [--task "description"]
```

**Output**:
- Current feature and stage
- Stage-specific guidance from graph
- Validation status
- Timestamp

**Example**:
```bash
$ uv run python3 -m ai_dev_graph.cli agent context --task "Add new API endpoint"

🤖 DEVELOPMENT CONTEXT
======================================================================
Task: Add new API endpoint
Timestamp: 2026-02-05T00:07:02

📍 Current Feature: db_persistence
   Title: Database Persistence Implementation
   Stage: TESTING

   📋 Stage Guidance:
   TESTING: Ejecutar suite completa de tests...

✓ Validation: PASS
```

### Get Suggested Actions

```bash
uv run python3 -m ai_dev_graph.cli agent suggest
```

**Output**:
- Prioritized action list
- Descriptions
- Specific commands to execute

**Example**:
```bash
$ uv run python3 -m ai_dev_graph.cli agent suggest

💡 SUGGESTED ACTIONS
======================================================================

1. 🔴 RUN_TESTS
   Execute full test suite and validate coverage
   Command: pytest --cov=ai_dev_graph

2. 🟡 VALIDATE_GRAPH
   Validate graph integrity
   Command: python -m ai_dev_graph.cli validate
```

### Validate Action Against Rules

```bash
uv run python3 -m ai_dev_graph.cli agent validate "action description"
```

**Output**:
- Validation result (PASS/FAIL)
- Rule violations (if any)
- Applicable rules
- Recommendations

**Example**:
```bash
$ uv run python3 -m ai_dev_graph.cli agent validate "skip testing stage"

🔍 VALIDATION RESULT
======================================================================
Action: skip testing stage
Valid: ❌ NO

❌ Violations:
   - PROHIBIDO saltar etapas de la cascada...

Recommendation: Fix violations before proceeding
```

### Get Coding Standards

```bash
uv run python3 -m ai_dev_graph.cli agent standards
```

**Output**:
- Core standards
- All rules from graph
- Instructions for agents

### Export Context for Agent

```bash
uv run python3 -m ai_dev_graph.cli agent export [--type claude] [--output file.json]
```

**Output**: JSON file with complete development context

**Default output**: `agent_context_{type}.json`

**Example**:
```bash
$ uv run python3 -m ai_dev_graph.cli agent export --type claude --output dev_context.json

✅ Agent context exported to: dev_context.json
   Agent type: claude
   Total nodes: 29
   Suggestions included: 2
```

## 🔧 Programmatic Usage

### Python API

```python
from ai_dev_graph.mcp_server import get_mcp_server

# Get MCP server instance
mcp = get_mcp_server()

# Get development context
context = mcp.get_development_context("Implement new feature")
print(f"Current stage: {context['current_feature']['current_stage']}")

# Get suggestions
suggestions = mcp.suggest_next_actions()
for sug in suggestions:
    print(f"- {sug['action']}: {sug['description']}")

# Validate action
result = mcp.validate_against_rules("skip testing")
if not result['is_valid']:
    print("Action violates rules!")

# Get coding standards
standards = mcp.get_coding_standards()
for rule in standards['rules']:
    print(f"- {rule['id']}: {rule['content']}")

# Export for agent
export = mcp.export_for_agent(agent_type="claude")
```

## 📊 Export Structure

The exported JSON contains:

```json
{
  "meta": {
    "export_time": "ISO timestamp",
    "agent_type": "claude",
    "graph_version": "enhanced_mcp_v1"
  },
  "philosophy": {
    "content": "Graph first development...",
    "principles": "GRAFO · PYTHON · API · DOC · TEST"
  },
  "methodology": {
    "type": "waterfall",
    "description": "Cascada con implementación continua",
    "stages": [...]
  },
  "standards": {
    "core": "Core coding standards",
    "rules": [...],
    "instructions": [...]
  },
  "current_context": {
    "status": "active",
    "feature_id": "...",
    "current_stage": "...",
    "stage_guidance": {...}
  },
  "suggestions": [...]
}
```

## 🎯 Use Cases

### 1. **Before Starting Work**

```bash
# Get current context
uv run python3 -m ai_dev_graph.cli agent context

# Get suggestions
uv run python3 -m ai_dev_graph.cli agent suggest

# Export full context
uv run python3 -m ai_dev_graph.cli agent export
```

### 2. **Validate Planned Actions**

```bash
# Validate before doing
uv run python3 -m ai_dev_graph.cli agent validate "implement without tests"

# Will show rule violations
```

### 3. **Get Standards Before Coding**

```bash
# Review all standards
uv run python3 -m ai_dev_graph.cli agent standards

# Follow the rules shown
```

### 4. **Agent-Assisted Development**

```bash
# 1. Export context
uv run python3 -m ai_dev_graph.cli agent export --output context.json

# 2. Use context.json to inform AI agent
# Agent now knows:
# - Current project state
# - Coding standards
# - Waterfall stage
# - Recommended actions
```

## 🌟 Advanced Features

### Custom Validation

```python
from ai_dev_graph.mcp_server import get_mcp_server

mcp = get_mcp_server()

# Validate with context
result = mcp.validate_against_rules(
    action="Add new endpoint",
    context={"module": "api", "tests_included": True}
)
```

### Search with Relevance

```python
# Search nodes with scoring
results = mcp.search_nodes("testing", node_type="rule", limit=5)

for node in results:
    print(f"{node['id']} (relevance: {node['relevance']})")
    print(f"  {node['content']}")
```

### Get Specific Node Context

```python
# Get node with depth
context = mcp.get_node("waterfall_methodology", depth=3)

print(f"Parents: {context['parents']}")
print(f"Children: {context['children']}")
print(f"Content: {context['content']}")
```

## 💡 Best Practices

1. **Check Context Before Work**
   ```bash
   uv run python3 -m ai_dev_graph.cli agent context
   ```

2. **Follow Suggestions**
   ```bash
   uv run python3 -m ai_dev_graph.cli agent suggest
   ```

3. **Validate Actions**
   ```bash
   uv run python3 -m ai_dev_graph.cli agent validate "your action"
   ```

4. **Export for AI Pair Programming**
   ```bash
   uv run python3 -m ai_dev_graph.cli agent export
   # Share context.json with AI
   ```

5. **Review Standards Regularly**
   ```bash
   uv run python3 -m ai_dev_graph.cli agent standards
   ```

## 🔄 Integration with Workflow

```bash
# Morning routine
uv run python3 -m ai_dev_graph.cli wf status
uv run python3 -m ai_dev_graph.cli agent suggest
uv run python3 -m ai_dev_graph.cli agent context

# Before coding
uv run python3 -m ai_dev_graph.cli agent standards
uv run python3 -m ai_dev_graph.cli agent export

# Before committing
uv run python3 -m ai_dev_graph.cli agent validate "commit and push"
uv run python3 -m ai_dev_graph.cli wf advance feature_id
```

## 📚 Related Commands

- `waterfall` / `wf` - Waterfall tracking
- `stats` - Graph statistics
- `validate` - Graph integrity
- `export` - Standard export
- `db` - Database management

## 🎨 Command Aliases

All agent commands support shortcuts:

```bash
# Full command
uv run python3 -m ai_dev_graph.cli agent suggest

# Alias
uv run python3 -m ai_dev_graph.cli ai suggest
```

---

**The Enhanced MCP Server brings AI-assisted development to your workflow** 🤖✨
