# AI Dev Graph MCP Server

[![PyPI version](https://badge.fury.io/py/ai-dev-graph-mcp.svg)](https://badge.fury.io/py/ai-dev-graph-mcp)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Advanced MCP (Model Context Protocol) Server for AI Dev Graph with enhanced graph navigation, semantic search, link prediction, and analysis capabilities.

## Features

🗺️ **Advanced Graph Navigation**
- BFS traversal with configurable depth and direction
- Shortest path finding between nodes
- All paths discovery with cycle detection
- Node neighborhood exploration

🔍 **Semantic Search**
- Intelligent scoring (exact match, word overlap, position-based)
- Multi-type filtering
- Metadata search support
- Related nodes discovery

🔗 **Link Prediction**
- Common neighbor analysis (Jaccard coefficient)
- Content similarity scoring
- Type compatibility bonuses
- Missing link suggestions with explanations

📊 **Graph Analysis**
- Node importance ranking (degree centrality)
- Community detection (connected components)
- Comprehensive graph metrics (density, avg degree, etc.)

🎨 **Rich CLI**
- Beautiful terminal UI with tables and trees
- Interactive graph exploration
- JSON export support

## Installation

### From PyPI

```bash
pip install ai-dev-graph-mcp
```

### From Source

```bash
# Clone the repository
git clone https://github.com/Dnllns/ai_dev_graph_project.git
cd ai_dev_graph_project/packages/ai_dev_graph_mcp

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

### Development Installation

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

## Quick Start

### Python API

```python
from ai_dev_graph_mcp import get_advanced_mcp_server

# Get the MCP server instance
mcp = get_advanced_mcp_server()

# Traverse the graph
result = mcp.traverse_graph("philosophy", max_depth=3, direction="both")
print(f"Visited {result['nodes_visited']} nodes")

# Semantic search
results = mcp.semantic_search("clean architecture", limit=10)
for r in results:
    print(f"Score: {r['score']} - {r['id']}")

# Find shortest path
path = mcp.find_shortest_path("source_node", "target_node")
print(f"Path: {' → '.join(path)}")

# Predict missing links
predictions = mcp.predict_missing_links(min_score=0.3)
for pred in predictions:
    print(f"{pred['source']} → {pred['target']} (score: {pred['score']:.3f})")

# Analyze node importance
importance = mcp.analyze_node_importance()
for node in importance[:10]:
    print(f"{node['id']}: {node['importance_score']}")
```

### CLI Usage

```bash
# Graph navigation
ai-graph-mcp traverse philosophy --depth 3 --direction both
ai-graph-mcp path source target --all
ai-graph-mcp neighborhood coding_standards --radius 2

# Search
ai-graph-mcp search "clean architecture" --type concept --limit 10
ai-graph-mcp related waterfall_methodology

# Link prediction
ai-graph-mcp predict-links --min-score 0.3 --limit 20
ai-graph-mcp suggest-links test_driven_development

# Analysis
ai-graph-mcp importance --limit 20
ai-graph-mcp communities
ai-graph-mcp metrics

# Export as JSON
ai-graph-mcp search "architecture" --json > results.json
```

## Documentation

Full documentation is available in the [docs](../../docs/ADVANCED_MCP.md) directory.

### Key Concepts

- **Traversal**: Navigate the graph using BFS with configurable parameters
- **Semantic Search**: Find nodes using intelligent scoring algorithms
- **Link Prediction**: Discover potential connections using graph algorithms
- **Graph Analysis**: Understand graph structure and node importance

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_dev_graph_mcp --cov-report=html

# Run specific test file
pytest tests/test_advanced_mcp.py -v
```

### Code Quality

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Building

```bash
# Build wheel
python -m build

# Install locally
pip install dist/ai_dev_graph_mcp-*.whl
```

## Architecture

The MCP server is built on top of the AI Dev Graph core library and provides:

1. **Advanced Navigation**: Sophisticated graph traversal algorithms
2. **Intelligent Search**: Semantic search with multi-factor scoring
3. **Predictive Analytics**: Link prediction using graph theory
4. **Structural Analysis**: Community detection and centrality metrics

## Contributing

Contributions are welcome! Please see the main repository's [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Links

- **Main Repository**: https://github.com/Dnllns/ai_dev_graph_project
- **Documentation**: [docs/ADVANCED_MCP.md](../../docs/ADVANCED_MCP.md)
- **Issues**: https://github.com/Dnllns/ai_dev_graph_project/issues
- **PyPI**: https://pypi.org/project/ai-dev-graph-mcp/

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
