#!/usr/bin/env python3
"""
AI Dev Graph - Main entry point and CLI

Usage:
    python -m ai_dev_graph.cli --help
"""

import argparse
import logging
import json
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
    logger.info("Saved to: graphs/v0_initial.json")


def cmd_validate(args):
    """Validate graph integrity."""
    from ai_dev_graph.application.manager import get_graph_manager

    logger.info("Validating graph...")
    manager = get_graph_manager()
    manager.load_or_create()

    report = manager.validate_graph()

    print("\n📊 VALIDATION REPORT")
    print("=" * 50)
    print(f"Valid: {report['valid']}")
    print(f"Total Nodes: {report['total_nodes']}")
    print(f"Total Edges: {report['total_edges']}")

    if report["issues"]:
        print("\n⚠️ ISSUES:")
        for issue in report["issues"]:
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
    from ai_dev_graph.application.manager import get_graph_manager

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

    if "node_types" in stats:
        print("\n📌 Nodes by Type:")
        for node_type, count in stats["node_types"].items():
            print(f"  - {node_type}: {count}")

    if stats.get("recommendations"):
        print("\n💡 Recommendations:")
        for rec in stats["recommendations"]:
            print(f"  - {rec}")


def cmd_export(args):
    """Export graph for agent consumption."""
    from ai_dev_graph.application.manager import get_graph_manager
    import json

    logger.info("Loading graph...")
    manager = get_graph_manager()
    manager.load_or_create()

    logger.info(f"Exporting for agent: {args.agent}")
    export = manager.export_for_agent(args.agent)

    output_path = args.output or f"graph_export_{args.agent}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    logger.info(f"Exported to: {output_path}")

    stats = export.get("statistics", {})
    print("\n✓ Export complete")
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
        with open(output, "w", encoding="utf-8") as f:
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
        backup_database,
        export_to_json,
        import_from_json,
        get_db_info,
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
            for node_type, count in info.get("node_types", {}).items():
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


def cmd_waterfall(args):
    """Waterfall tracking commands."""
    from ai_dev_graph.waterfall_tracker import WaterfallTracker, WaterfallStage

    tracker = WaterfallTracker()

    if args.wf_action == "start":
        feature = tracker.start_feature(args.feature_id, args.title)
        print(f"\n🚀 Started tracking feature: {feature.feature_id}")
        print(f"Title: {feature.title}")
        print(f"Stage: {feature.current_stage.value.upper()}")
        print(f"Started: {feature.started_at}\n")

    elif args.wf_action == "status":
        if args.feature:
            feature = tracker.get_feature(args.feature)
            if not feature:
                print(f"\n❌ Feature not found: {args.feature}\n")
                return

            print(f"\n📍 FEATURE STATUS: {feature.feature_id}")
            print("=" * 60)
            print(f"Title: {feature.title}")
            print(f"Current Stage: {feature.current_stage.value.upper()}")
            print(f"Started: {feature.started_at}")
            print(f"Last Updated: {feature.updated_at}")

            if feature.stage_history:
                print("\n📋 Completed Stages:")
                for entry in feature.stage_history:
                    print(f"  ✅ {entry['stage'].upper()} - {entry['completed_at']}")

            if feature.notes:
                print(f"\n📝 Notes:\n{feature.notes}")
            print()
        else:
            current = tracker.get_current_feature()
            if not current:
                print("\n❌ No features being tracked.\n")
                return

            print(f"\n📍 CURRENT FEATURE: {current.feature_id}")
            print("=" * 60)
            print(f"Title: {current.title}")
            print(f"Stage: {current.current_stage.value.upper()}")
            print(f"Updated: {current.updated_at}\n")

    elif args.wf_action == "advance":
        feature = tracker.get_feature(args.feature_id)
        if not feature:
            print(f"\n❌ Feature not found: {args.feature_id}\n")
            return

        old_stage = feature.current_stage.value
        if tracker.advance_feature(args.feature_id):
            feature = tracker.get_feature(args.feature_id)
            print(f"\n✅ Advanced feature: {args.feature_id}")
            print(f"   {old_stage.upper()} → {feature.current_stage.value.upper()}\n")
        else:
            print("\n❌ Cannot advance (already at final stage)\n")

    elif args.wf_action == "regress":
        feature = tracker.get_feature(args.feature_id)
        if not feature:
            print(f"\n❌ Feature not found: {args.feature_id}\n")
            return

        old_stage = feature.current_stage.value
        reason = args.reason or "Issues found"
        if tracker.regress_feature(args.feature_id, reason):
            feature = tracker.get_feature(args.feature_id)
            print(f"\n⚠️  Regressed feature: {args.feature_id}")
            print(f"   {old_stage.upper()} → {feature.current_stage.value.upper()}")
            print(f"   Reason: {reason}\n")
        else:
            print("\n❌ Cannot regress (already at first stage)\n")

    elif args.wf_action == "note":
        if tracker.get_feature(args.feature_id):
            tracker.update_notes(args.feature_id, args.note)
            print(f"\n✓ Note added to {args.feature_id}\n")
        else:
            print(f"\n❌ Feature not found: {args.feature_id}\n")

    elif args.wf_action == "list":
        stage_filter = WaterfallStage(args.stage) if args.stage else None
        features = tracker.list_features(stage=stage_filter)

        if not features:
            print("\n📋 No features found.\n")
            return

        print(f"\n📋 FEATURES ({len(features)})")
        print("=" * 80)

        for f in features:
            status_icon = "🔄" if f.current_stage.value != "completed" else "✅"
            print(f"{status_icon} {f.feature_id}")
            print(f"   Title: {f.title}")
            print(f"   Stage: {f.current_stage.value.upper()}")
            print(f"   Updated: {f.updated_at}")
            print()

    elif args.wf_action == "stats":
        stats = tracker.get_stats()
        print("\n📊 WATERFALL STATISTICS")
        print("=" * 50)
        print(f"Total Features: {stats['total_features']}")
        print(f"Active Features: {stats['active_features']}")
        print("\nBy Stage:")
        for stage, count in stats["by_stage"].items():
            if count > 0:
                print(f"  {stage.upper()}: {count}")
        print()


def cmd_agent(args):
    """Enhanced MCP agent assistance commands."""
    from ai_dev_graph.mcp_server import get_mcp_server

    mcp = get_mcp_server()

    if args.agent_action == "context":
        # Get development context
        task = args.task if hasattr(args, "task") else "General development"
        context = mcp.get_development_context(task)

        print("\n🤖 DEVELOPMENT CONTEXT")
        print("=" * 70)
        print(f"Task: {context['task']}")
        print(f"Timestamp: {context['timestamp']}\n")

        # Current feature
        feature = context["current_feature"]
        if feature["status"] == "active":
            print(f"📍 Current Feature: {feature['feature_id']}")
            print(f"   Title: {feature['title']}")
            print(f"   Stage: {feature['current_stage'].upper()}")
            if feature.get("stage_guidance"):
                print("\n   📋 Stage Guidance:")
                print(f"   {feature['stage_guidance']['guidance']}")
        else:
            print(f"⚠️  {feature['message']}")

        # Validation
        validation = context["validation"]
        print(f"\n✓ Validation: {'PASS' if validation['is_valid'] else 'FAIL'}")
        if validation["violations"]:
            print("   Violations:")
            for v in validation["violations"]:
                print(f"   - [{v['severity'].upper()}] {v['message']}")

        print()

    elif args.agent_action == "suggest":
        # Get suggested actions
        suggestions = mcp.suggest_next_actions()

        print("\n💡 SUGGESTED ACTIONS")
        print("=" * 70)

        for i, sug in enumerate(suggestions, 1):
            priority_icon = "🔴" if sug["priority"] == "high" else "🟡"
            print(f"\n{i}. {priority_icon} {sug['action'].upper()}")
            print(f"   {sug['description']}")
            print(f"   Command: {sug['command']}")

        print()

    elif args.agent_action == "validate":
        # Validate action against rules
        action = args.action if hasattr(args, "action") else "unknown action"
        result = mcp.validate_against_rules(action)

        print("\n🔍 VALIDATION RESULT")
        print("=" * 70)
        print(f"Action: {result['action']}")
        print(f"Valid: {'✅ YES' if result['is_valid'] else '❌ NO'}\n")

        if result["violations"]:
            print("❌ Violations:")
            for v in result["violations"]:
                print(f"   - {v['message']}")
            print()

        if result["applicable_rules"]:
            print("📋 Applicable Rules:")
            for r in result["applicable_rules"]:
                print(f"   - [{r['type']}] {r['content']}")
            print()

        print(f"Recommendation: {result['recommendation']}\n")

    elif args.agent_action == "standards":
        # Get coding standards
        standards = mcp.get_coding_standards()

        print("\n📐 CODING STANDARDS")
        print("=" * 70)

        if "core" in standards and standards["core"]:
            print(f"\nCore Standards:\n{standards['core']}\n")

        if standards.get("rules"):
            print("Rules:")
            for rule in standards["rules"][:10]:  # Limit to 10
                print(f"  • {rule['id']}: {rule['content'][:80]}...")

        if standards.get("instructions"):
            print("\nInstructions:")
            for inst in standards["instructions"]:
                print(f"  • {inst['id']}: {inst['content'][:80]}...")

        print()

    elif args.agent_action == "export":
        # Export for agent
        agent_type = args.type if hasattr(args, "type") else "claude"
        export = mcp.export_for_agent(agent_type)
        output = (
            args.output
            if hasattr(args, "output")
            else f"agent_context_{agent_type}.json"
        )

        with open(output, "w") as f:
            json.dump(export, f, indent=2)

        print(f"\n✅ Agent context exported to: {output}")
        print(f"   Agent type: {agent_type}")
        print(f"   Total nodes: {export['graph_structure']['total_nodes']}")
        print(f"   Suggestions included: {len(export['suggestions'])}\n")


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
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Server command
    server_parser = subparsers.add_parser("server", help="Start API server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Server host")
    server_parser.add_argument("--port", type=int, default=8000, help="Server port")
    server_parser.add_argument(
        "--reload", action="store_true", help="Auto-reload on changes"
    )
    server_parser.set_defaults(func=cmd_server)

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize graph")
    init_parser.set_defaults(func=cmd_init)

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate graph")
    validate_parser.set_defaults(func=cmd_validate)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.set_defaults(func=cmd_stats)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export graph")
    export_parser.add_argument("--agent", default="default", help="Target agent type")
    export_parser.add_argument("--output", help="Output file path")
    export_parser.set_defaults(func=cmd_export)

    # MCP command
    mcp_parser = subparsers.add_parser("mcp", help="MCP server for AI agents")
    mcp_subparsers = mcp_parser.add_subparsers(dest="action", help="MCP action")

    mcp_info = mcp_subparsers.add_parser("info", help="Show project overview")
    mcp_info.set_defaults(func=cmd_mcp)

    mcp_search = mcp_subparsers.add_parser("search", help="Search nodes")
    mcp_search.add_argument("query", help="Search query")
    mcp_search.add_argument("--type", help="Filter by node type")
    mcp_search.set_defaults(func=cmd_mcp)

    mcp_graph = mcp_subparsers.add_parser("graph", help="Export graph for MCP")
    mcp_graph.add_argument("--output", help="Output file path")
    mcp_graph.set_defaults(func=cmd_mcp)

    mcp_rules = mcp_subparsers.add_parser("rules", help="Show rules and standards")
    mcp_rules.set_defaults(func=cmd_mcp)

    # Database command
    db_parser = subparsers.add_parser("db", help="Database management")
    db_subparsers = db_parser.add_subparsers(dest="db_action", help="Database action")

    db_info = db_subparsers.add_parser("info", help="Show database info")
    db_info.set_defaults(func=cmd_db)

    db_backup = db_subparsers.add_parser("backup", help="Backup database")
    db_backup.set_defaults(func=cmd_db)

    db_export = db_subparsers.add_parser("export", help="Export to JSON")
    db_export.add_argument("--output", default="graphs/export.json", help="Output file")
    db_export.set_defaults(func=cmd_db)

    db_import = db_subparsers.add_parser("import", help="Import from JSON")
    db_import.add_argument("json_file", help="JSON file to import")
    db_import.add_argument("--clear", action="store_true", help="Clear existing data")
    db_import.set_defaults(func=cmd_db)

    # Waterfall tracker command
    wf_parser = subparsers.add_parser(
        "waterfall", aliases=["wf"], help="Waterfall stage tracking"
    )
    wf_subparsers = wf_parser.add_subparsers(dest="wf_action", help="Waterfall action")

    wf_start = wf_subparsers.add_parser("start", help="Start tracking new feature")
    wf_start.add_argument("feature_id", help="Feature identifier")
    wf_start.add_argument("title", help="Feature title")
    wf_start.set_defaults(func=cmd_waterfall)

    wf_status = wf_subparsers.add_parser("status", help="Show current status")
    wf_status.add_argument("--feature", help="Specific feature ID")
    wf_status.set_defaults(func=cmd_waterfall)

    wf_advance = wf_subparsers.add_parser("advance", help="Advance to next stage")
    wf_advance.add_argument("feature_id", help="Feature to advance")
    wf_advance.set_defaults(func=cmd_waterfall)

    wf_regress = wf_subparsers.add_parser("regress", help="Go back to previous stage")
    wf_regress.add_argument("feature_id", help="Feature to regress")
    wf_regress.add_argument("--reason", help="Reason for regression")
    wf_regress.set_defaults(func=cmd_waterfall)

    wf_note = wf_subparsers.add_parser("note", help="Add note to feature")
    wf_note.add_argument("feature_id", help="Feature ID")
    wf_note.add_argument("note", help="Note text")
    wf_note.set_defaults(func=cmd_waterfall)

    wf_list = wf_subparsers.add_parser("list", help="List all features")
    wf_list.add_argument("--stage", help="Filter by stage")
    wf_list.set_defaults(func=cmd_waterfall)

    wf_stats = wf_subparsers.add_parser("stats", help="Show statistics")
    wf_stats.set_defaults(func=cmd_waterfall)

    # Agent assistance command (Enhanced MCP)
    agent_parser = subparsers.add_parser(
        "agent", aliases=["ai"], help="AI agent assistance (Enhanced MCP)"
    )
    agent_subparsers = agent_parser.add_subparsers(
        dest="agent_action", help="Agent action"
    )

    agent_context = agent_subparsers.add_parser(
        "context", help="Get development context"
    )
    agent_context.add_argument(
        "--task", help="Task description", default="General development"
    )
    agent_context.set_defaults(func=cmd_agent)

    agent_suggest = agent_subparsers.add_parser(
        "suggest", help="Get suggested next actions"
    )
    agent_suggest.set_defaults(func=cmd_agent)

    agent_validate = agent_subparsers.add_parser(
        "validate", help="Validate action against rules"
    )
    agent_validate.add_argument("action", help="Action to validate")
    agent_validate.set_defaults(func=cmd_agent)

    agent_standards = agent_subparsers.add_parser(
        "standards", help="Get coding standards"
    )
    agent_standards.set_defaults(func=cmd_agent)

    agent_export = agent_subparsers.add_parser(
        "export", help="Export context for agent"
    )
    agent_export.add_argument("--type", help="Agent type", default="claude")
    agent_export.add_argument("--output", help="Output file")
    agent_export.set_defaults(func=cmd_agent)

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


if __name__ == "__main__":
    sys.exit(main())
