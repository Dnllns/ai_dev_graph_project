"""Advanced CLI commands for graph exploration and analysis."""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel

from ai_dev_graph_mcp.server import get_advanced_mcp_server

console = Console()


@click.group(name="graph")
def main():
    """Advanced graph exploration and analysis commands."""
    pass


@graph_commands.command(name="traverse")
@click.argument("start_node")
@click.option("--depth", "-d", default=3, help="Maximum traversal depth")
@click.option(
    "--direction",
    "-dir",
    type=click.Choice(["forward", "backward", "both"]),
    default="both",
    help="Traversal direction",
)
@click.option("--type", "-t", help="Filter by node type")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def traverse_graph(start_node, depth, direction, type, output_json):
    """Traverse the graph from a starting node."""
    mcp = get_advanced_mcp_server()

    node_filter = {"type": type} if type else None
    result = mcp.traverse_graph(start_node, max_depth=depth, direction=direction, node_filter=node_filter)

    if output_json:
        click.echo(json.dumps(result, indent=2))
        return

    console.print(f"\n[bold cyan]Graph Traversal from {start_node}[/bold cyan]")
    console.print(f"Direction: {direction}, Max Depth: {depth}")
    console.print(f"Nodes Visited: {result['nodes_visited']}\n")

    for depth_level, nodes in result["nodes_by_depth"].items():
        console.print(f"[bold yellow]Depth {depth_level}:[/bold yellow]")
        for node in nodes:
            console.print(f"  • {node['id']} ({node['type']})")
            console.print(f"    {node['content'][:80]}...")
        console.print()


@graph_commands.command(name="path")
@click.argument("source")
@click.argument("target")
@click.option("--all", "find_all", is_flag=True, help="Find all paths")
@click.option("--max-paths", default=5, help="Maximum paths to find")
def find_path(source, target, find_all, max_paths):
    """Find path(s) between two nodes."""
    mcp = get_advanced_mcp_server()

    if find_all:
        paths = mcp.find_all_paths(source, target, max_paths=max_paths)
        if not paths:
            console.print(f"[red]No paths found between {source} and {target}[/red]")
            return

        console.print(f"\n[bold cyan]Found {len(paths)} path(s):[/bold cyan]\n")
        for i, path in enumerate(paths, 1):
            console.print(f"[yellow]Path {i}:[/yellow] {' → '.join(path)}")
    else:
        path = mcp.find_shortest_path(source, target)
        if not path:
            console.print(f"[red]No path found between {source} and {target}[/red]")
            return

        console.print(f"\n[bold cyan]Shortest Path:[/bold cyan]")
        console.print(f"{' → '.join(path)}")
        console.print(f"\n[green]Length: {len(path) - 1} edges[/green]")


@graph_commands.command(name="neighborhood")
@click.argument("node_id")
@click.option("--radius", "-r", default=1, help="Neighborhood radius")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def show_neighborhood(node_id, radius, output_json):
    """Show the neighborhood of a node."""
    mcp = get_advanced_mcp_server()
    neighborhood = mcp.get_node_neighborhood(node_id, radius=radius)

    if output_json:
        click.echo(json.dumps(neighborhood, indent=2))
        return

    console.print(f"\n[bold cyan]Neighborhood of {node_id}[/bold cyan]")
    console.print(f"Radius: {radius}\n")

    # Create tree visualization
    tree = Tree(f"[bold]{node_id}[/bold]")

    nodes_by_depth = {}
    for node_id, node_data in neighborhood["nodes"].items():
        depth = node_data["depth"]
        if depth not in nodes_by_depth:
            nodes_by_depth[depth] = []
        nodes_by_depth[depth].append((node_id, node_data))

    for depth in sorted(nodes_by_depth.keys()):
        if depth == 0:
            continue
        for node_id, node_data in nodes_by_depth[depth]:
            tree.add(f"{node_id} ({node_data['type']})")

    console.print(tree)
    console.print(f"\n[green]Total nodes: {len(neighborhood['nodes'])}[/green]")
    console.print(f"[green]Total edges: {len(neighborhood['edges'])}[/green]")


@graph_commands.command(name="search")
@click.argument("query")
@click.option("--type", "-t", multiple=True, help="Filter by node type(s)")
@click.option("--limit", "-l", default=10, help="Maximum results")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def semantic_search(query, type, limit, output_json):
    """Perform semantic search on the graph."""
    mcp = get_advanced_mcp_server()

    node_types = list(type) if type else None
    results = mcp.semantic_search(query, node_types=node_types, limit=limit)

    if output_json:
        click.echo(json.dumps(results, indent=2))
        return

    if not results:
        console.print(f"[yellow]No results found for '{query}'[/yellow]")
        return

    console.print(f"\n[bold cyan]Search Results for '{query}'[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Score", style="cyan", width=8)
    table.add_column("ID", style="green", width=25)
    table.add_column("Type", style="yellow", width=12)
    table.add_column("Content", style="white")

    for result in results:
        content_preview = result["content"][:60] + "..." if len(result["content"]) > 60 else result["content"]
        table.add_row(
            str(result["score"]),
            result["id"],
            result["type"],
            content_preview
        )

    console.print(table)


@graph_commands.command(name="related")
@click.argument("node_id")
@click.option("--limit", "-l", default=10, help="Maximum results")
def find_related(node_id, limit):
    """Find nodes related to a given node."""
    mcp = get_advanced_mcp_server()
    related = mcp.find_related_nodes(node_id, max_results=limit)

    if not related:
        console.print(f"[yellow]No related nodes found for {node_id}[/yellow]")
        return

    console.print(f"\n[bold cyan]Nodes Related to {node_id}[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Relatedness", style="cyan", width=12)
    table.add_column("ID", style="green", width=25)
    table.add_column("Type", style="yellow", width=12)
    table.add_column("Content", style="white")

    for node in related:
        content_preview = node["content"][:50] + "..." if len(node["content"]) > 50 else node["content"]
        table.add_row(
            str(node["relatedness_score"]),
            node["id"],
            node["type"],
            content_preview
        )

    console.print(table)


@graph_commands.command(name="predict-links")
@click.option("--min-score", default=0.3, help="Minimum prediction score")
@click.option("--limit", "-l", default=20, help="Maximum predictions")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def predict_links(min_score, limit, output_json):
    """Predict missing links in the graph."""
    mcp = get_advanced_mcp_server()
    predictions = mcp.predict_missing_links(min_score=min_score, max_predictions=limit)

    if output_json:
        click.echo(json.dumps(predictions, indent=2))
        return

    if not predictions:
        console.print("[yellow]No link predictions found[/yellow]")
        return

    console.print(f"\n[bold cyan]Link Predictions (min score: {min_score})[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Score", style="cyan", width=8)
    table.add_column("Source", style="green", width=20)
    table.add_column("Target", style="green", width=20)
    table.add_column("Reason", style="white")

    for pred in predictions:
        table.add_row(
            str(pred["score"]),
            f"{pred['source']} ({pred['source_type']})",
            f"{pred['target']} ({pred['target_type']})",
            pred["reason"]
        )

    console.print(table)


@graph_commands.command(name="suggest-links")
@click.argument("node_id")
@click.option("--limit", "-l", default=5, help="Maximum suggestions")
def suggest_links(node_id, limit):
    """Suggest new links for a specific node."""
    mcp = get_advanced_mcp_server()
    suggestions = mcp.suggest_new_links(node_id, max_suggestions=limit)

    if not suggestions:
        console.print(f"[yellow]No link suggestions for {node_id}[/yellow]")
        return

    console.print(f"\n[bold cyan]Link Suggestions for {node_id}[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Score", style="cyan", width=8)
    table.add_column("Target", style="green", width=25)
    table.add_column("Type", style="yellow", width=12)
    table.add_column("Reason", style="white")

    for sugg in suggestions:
        table.add_row(
            str(sugg["score"]),
            sugg["target"],
            sugg["target_type"],
            sugg["reason"]
        )

    console.print(table)


@graph_commands.command(name="importance")
@click.option("--limit", "-l", default=20, help="Number of nodes to show")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def analyze_importance(limit, output_json):
    """Analyze and rank nodes by importance."""
    mcp = get_advanced_mcp_server()
    importance = mcp.analyze_node_importance()[:limit]

    if output_json:
        click.echo(json.dumps(importance, indent=2))
        return

    console.print(f"\n[bold cyan]Node Importance Analysis (Top {limit})[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="cyan", width=6)
    table.add_column("Score", style="cyan", width=8)
    table.add_column("ID", style="green", width=25)
    table.add_column("Type", style="yellow", width=12)
    table.add_column("In/Out", style="white", width=10)

    for i, node in enumerate(importance, 1):
        table.add_row(
            str(i),
            str(node["importance_score"]),
            node["id"],
            node["type"],
            f"{node['in_degree']}/{node['out_degree']}"
        )

    console.print(table)


@graph_commands.command(name="communities")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def detect_communities(output_json):
    """Detect communities/clusters in the graph."""
    mcp = get_advanced_mcp_server()
    communities = mcp.detect_communities()

    if output_json:
        click.echo(json.dumps(communities, indent=2))
        return

    console.print(f"\n[bold cyan]Detected Communities[/bold cyan]\n")

    for community_id, nodes in communities.items():
        panel = Panel(
            f"[green]{len(nodes)} nodes:[/green]\n" + "\n".join(f"  • {node}" for node in nodes[:10]) +
            (f"\n  ... and {len(nodes) - 10} more" if len(nodes) > 10 else ""),
            title=f"[bold]{community_id}[/bold]",
            border_style="cyan"
        )
        console.print(panel)


@graph_commands.command(name="metrics")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def show_metrics(output_json):
    """Show comprehensive graph metrics."""
    mcp = get_advanced_mcp_server()
    metrics = mcp.get_graph_metrics()

    if output_json:
        click.echo(json.dumps(metrics, indent=2))
        return

    console.print("\n[bold cyan]Graph Metrics[/bold cyan]\n")

    # Basic metrics
    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="yellow", width=20)
    table.add_column("Value", style="green")

    table.add_row("Total Nodes", str(metrics["total_nodes"]))
    table.add_row("Total Edges", str(metrics["total_edges"]))
    table.add_row("Average Degree", str(metrics["average_degree"]))
    table.add_row("Max Degree", str(metrics["max_degree"]))
    table.add_row("Min Degree", str(metrics["min_degree"]))
    table.add_row("Density", f"{metrics['density']:.4f}")

    console.print(table)

    # Node types
    console.print("\n[bold yellow]Node Types:[/bold yellow]")
    for node_type, count in metrics["node_types"].items():
        console.print(f"  • {node_type}: {count}")


if __name__ == "__main__":
    main()
