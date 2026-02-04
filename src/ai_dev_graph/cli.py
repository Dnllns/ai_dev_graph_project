#!/usr/bin/env python3
"""
AI Dev Graph - Main entry point and CLI

Usage:
    python -m ai_dev_graph.cli --help
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_server(args):
    """Start the API server."""
    import uvicorn
    from ai_dev_graph.api.main import app
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info(f"Admin panel: http://{args.host}:{args.port}/admin")
    logger.info(f"API docs: http://{args.host}:{args.port}/docs")
    
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)


def cmd_init(args):
    """Initialize project graph."""
    from ai_dev_graph.init_meta_graph import init_project_graph
    
    logger.info("Initializing project graph...")
    kg = init_project_graph()
    
    stats = kg.get_graph_stats()
    logger.info(f"Graph initialized with {stats['total_nodes']} nodes")
    logger.info(f"Saved to: graphs/v0_initial.json")


def cmd_validate(args):
    """Validate graph integrity."""
    from ai_dev_graph.models.manager import get_graph_manager
    
    logger.info("Validating graph...")
    manager = get_graph_manager()
    manager.load_or_create()
    
    report = manager.validate_graph()
    
    print("\n📊 VALIDATION REPORT")
    print("=" * 50)
    print(f"Valid: {report['valid']}")
    print(f"Total Nodes: {report['total_nodes']}")
    print(f"Total Edges: {report['total_edges']}")
    
    if report['issues']:
        print("\n⚠️ ISSUES:")
        for issue in report['issues']:
            print(f"  - {issue}")
    else:
        print("\n✓ No issues found")
    
    recommendations = manager.get_recommendations()
    if recommendations:
        print("\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  - {rec}")


def cmd_stats(args):
    """Show graph statistics."""
    from ai_dev_graph.models.manager import get_graph_manager
    
    logger.info("Loading graph...")
    manager = get_graph_manager()
    manager.load_or_create()
    
    stats = manager.get_statistics()
    
    print("\n📈 GRAPH STATISTICS")
    print("=" * 50)
    print(f"Total Nodes: {stats['total_nodes']}")
    print(f"Total Edges: {stats['total_edges']}")
    print(f"Density: {stats['density']:.4f}")
    print(f"Average Degree: {stats.get('average_degree', 'N/A')}")
    
    if 'node_types' in stats:
        print("\n📌 Nodes by Type:")
        for node_type, count in stats['node_types'].items():
            print(f"  - {node_type}: {count}")
    
    if stats.get('recommendations'):
        print("\n💡 Recommendations:")
        for rec in stats['recommendations']:
            print(f"  - {rec}")


def cmd_export(args):
    """Export graph for agent consumption."""
    from ai_dev_graph.models.manager import get_graph_manager
    import json
    
    logger.info("Loading graph...")
    manager = get_graph_manager()
    manager.load_or_create()
    
    logger.info(f"Exporting for agent: {args.agent}")
    export = manager.export_for_agent(args.agent)
    
    output_path = args.output or f"graph_export_{args.agent}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Exported to: {output_path}")
    
    stats = export.get('statistics', {})
    print(f"\n✓ Export complete")
    print(f"  Nodes: {stats.get('total_nodes', 'N/A')}")
    print(f"  Edges: {stats.get('total_edges', 'N/A')}")


def cmd_mcp(args):
    """Start MCP server for AI agent integration."""
    from ai_dev_graph.mcp_server import create_mcp_server
    import json
    
    logger.info("Initializing MCP server...")
    mcp = create_mcp_server()
    
    if args.action == "info":
        # Show project overview
        overview = mcp.get_project_overview()
        print("\n📊 PROJECT OVERVIEW (MCP)")
        print("=" * 50)
        print(json.dumps(overview, indent=2, ensure_ascii=False))
    
    elif args.action == "search":
        # Search nodes
        results = mcp.search_nodes(args.query, args.type)
        print(f"\n🔍 Search Results for '{args.query}'")
        print("=" * 50)
        if results:
            for result in results:
                print(f"\n  ID: {result['id']}")
                print(f"  Type: {result['type']}")
                print(f"  Content: {result['content'][:100]}...")
        else:
            print("No results found")
    
    elif args.action == "graph":
        # Export complete graph for MCP
        export = mcp.export_for_agent()
        output = args.output or "graph_mcp.json"
        with open(output, 'w', encoding='utf-8') as f:
            f.write(export)
        logger.info(f"Graph exported to: {output}")
    
    elif args.action == "rules":
        # Show rules and standards
        rules = mcp.get_rules_and_standards()
        print("\n⚖️ RULES & STANDARDS")
        print("=" * 50)
        for rule in rules:
            print(f"\n  {rule['id']} ({rule['type']})")
            print(f"  {rule['content']}")


def cmd_db(args):
    """Database management commands."""
    from ai_dev_graph.core.db_utils import (
        backup_database, export_to_json, import_from_json, get_db_info
    )
    
    if args.db_action == "info":
        info = get_db_info()
        print("\\n📊 DATABASE INFO")
        print("=" * 50)
        if info["exists"]:
            print(f"Path: {info['path']}")
            print(f"Size: {info['size_mb']} MB ({info['size_bytes']} bytes)")
            print(f"Total Nodes: {info['total_nodes']}")
            print(f"Total Edges: {info['total_edges']}")
            print("\\nNode Types:")
            for node_type, count in info.get('node_types', {}).items():
                print(f"  - {node_type}: {count}")
        else:
            print("Database does not exist yet.")
    
    elif args.db_action == "backup":
        backup_path = backup_database()
        print(f"\\n✓ Database backed up to: {backup_path}")
    
    elif args.db_action == "export":
        export_to_json(output_path=args.output)
        print(f"\\n✓ Graph exported to: {args.output}")
    
    elif args.db_action == "import":
        import_from_json(args.json_file, clear_existing=args.clear)
        print(f"\\n✓ Graph imported from: {args.json_file}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Dev Graph - Knowledge graph for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ai_dev_graph.cli server                 # Start API server
  python -m ai_dev_graph.cli init                   # Initialize graph
  python -m ai_dev_graph.cli stats                  # Show statistics
  python -m ai_dev_graph.cli validate               # Validate graph
  python -m ai_dev_graph.cli export --agent claude  # Export for Claude
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start API server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Server host')
    server_parser.add_argument('--port', type=int, default=8000, help='Server port')
    server_parser.add_argument('--reload', action='store_true', help='Auto-reload on changes')
    server_parser.set_defaults(func=cmd_server)
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize graph')
    init_parser.set_defaults(func=cmd_init)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate graph')
    validate_parser.set_defaults(func=cmd_validate)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.set_defaults(func=cmd_stats)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export graph')
    export_parser.add_argument('--agent', default='default', help='Target agent type')
    export_parser.add_argument('--output', help='Output file path')
    export_parser.set_defaults(func=cmd_export)
    
    # MCP command
    mcp_parser = subparsers.add_parser('mcp', help='MCP server for AI agents')
    mcp_subparsers = mcp_parser.add_subparsers(dest='action', help='MCP action')
    
    mcp_info = mcp_subparsers.add_parser('info', help='Show project overview')
    mcp_info.set_defaults(func=cmd_mcp)
    
    mcp_search = mcp_subparsers.add_parser('search', help='Search nodes')
    mcp_search.add_argument('query', help='Search query')
    mcp_search.add_argument('--type', help='Filter by node type')
    mcp_search.set_defaults(func=cmd_mcp)
    
    mcp_graph = mcp_subparsers.add_parser('graph', help='Export graph for MCP')
    mcp_graph.add_argument('--output', help='Output file path')
    mcp_graph.set_defaults(func=cmd_mcp)
    
    mcp_rules = mcp_subparsers.add_parser('rules', help='Show rules and standards')
    mcp_rules.set_defaults(func=cmd_mcp)
    
    # Database command
    db_parser = subparsers.add_parser('db', help='Database management')
    db_subparsers = db_parser.add_subparsers(dest='db_action', help='Database action')
    
    db_info = db_subparsers.add_parser('info', help='Show database info')
    db_info.set_defaults(func=cmd_db)
    
    db_backup = db_subparsers.add_parser('backup', help='Backup database')
    db_backup.set_defaults(func=cmd_db)
    
    db_export = db_subparsers.add_parser('export', help='Export to JSON')
    db_export.add_argument('--output', default='graphs/export.json', help='Output file')
    db_export.set_defaults(func=cmd_db)
    
    db_import = db_subparsers.add_parser('import', help='Import from JSON')
    db_import.add_argument('json_file', help='JSON file to import')
    db_import.add_argument('--clear', action='store_true', help='Clear existing data')
    db_import.set_defaults(func=cmd_db)
    
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    try:
        args.func(args)
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
