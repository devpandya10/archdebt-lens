"""
Command-Line Interface (CLI) for ArchDebt-Lens.
Provides terminal commands for scanning repos, evaluating PRs, and computing stats.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from archdebt_lens import __version__
from archdebt_lens.graph.dependency import DependencyGraphBuilder
from archdebt_lens.graph.metrics import MetricsCalculator
from archdebt_lens.guardrail.pr_checker import PRGuardrailChecker
from archdebt_lens.replication.compare_paper import PaperMetricsComparator

app = typer.Typer(
    name="atd-lens",
    help="ArchDebt-Lens: Automated Architectural Technical Debt Lifecycle & Dependency Evolution Platform",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Display tool version and research paper attribution."""
    meta_text = (
        "[dim]Based on: 'Tracing the Lifecycle of Architecture Technical Debt in "
        "Software Systems: A Dependency Approach' (Sutoyo et al., 2025)[/dim]"
    )
    console.print(
        Panel(
            f"[bold green]ArchDebt-Lens v{__version__}[/bold green]\n"
            "[white]Automated Architectural Technical Debt Lifecycle Platform[/white]\n"
            f"{meta_text}",
            title="ArchDebt-Lens",
        )
    )


@app.command()
def compare_paper(
    output: Optional[str] = typer.Option(
        "PAPER_METRICS_COMPARISON.md",
        "--output",
        "-o",
        help="Path to generate markdown comparison report",
    )
):
    """Run direct empirical verification and metric comparison against Sutoyo et al. (2025)."""
    comparator = PaperMetricsComparator()
    comparator.print_terminal_report()
    if output:
        out_path = comparator.generate_markdown_report(output)
        console.print(f"[bold green]✓ Detailed markdown report written to:[/bold green] {out_path}")


@app.command()
def scan(
    path: str = typer.Option(".", "--path", "-p", help="Directory containing source files to scan"),
    extension: str = typer.Option(".java", "--ext", "-e", help="File extension to scan (.java, .py)"),
):
    """Scan a codebase, build class dependency graph, and display connectivity metrics."""
    dir_path = Path(path).resolve()
    if not dir_path.exists():
        console.print(f"[bold red]Error:[/bold red] Directory '{dir_path}' does not exist.")
        raise typer.Exit(1)

    console.print(f"[bold cyan]Scanning directory:[/bold cyan] {dir_path} for '{extension}' files...")

    builder = DependencyGraphBuilder()
    files_found = list(dir_path.rglob(f"*{extension}"))

    if not files_found:
        console.print(f"[yellow]No '{extension}' files found in {dir_path}.[/yellow]")
        return

    for f in files_found:
        rel_path = str(f.relative_to(dir_path))
        builder.add_file(rel_path, f.read_text(encoding="utf-8", errors="ignore"))

    builder.build_edges()
    metrics = MetricsCalculator.calculate_all_metrics(builder)
    summary = MetricsCalculator.calculate_summary_stats(metrics)

    table = Table(title=f"Architectural Dependency Metrics (Files: {int(summary['file_count'])})")
    table.add_column("File Path", style="cyan")
    table.add_column("FAN-IN", justify="right", style="green")
    table.add_column("FAN-OUT", justify="right", style="blue")
    table.add_column("SLOC", justify="right")
    table.add_column("Complexity", justify="right", style="magenta")
    table.add_column("FAN-IN/SLOC", justify="right")

    for fpath, m in sorted(metrics.items(), key=lambda x: x[1].fan_in, reverse=True)[:15]:
        table.add_row(
            fpath,
            str(m.fan_in),
            str(m.fan_out),
            str(m.sloc),
            f"{m.cyclomatic_complexity:.1f}",
            f"{m.fan_in_per_sloc:.4f}",
        )

    console.print(table)
    console.print(
        f"[bold]Summary:[/bold] Avg FAN-IN: [green]{summary['fan_in_avg']:.2f}[/green] | "
        f"Max FAN-IN: [green]{summary['fan_in_max']:.0f}[/green] | "
        f"Avg FAN-OUT: [blue]{summary['fan_out_avg']:.2f}[/blue] | "
        f"Max FAN-OUT: [blue]{summary['fan_out_max']:.0f}[/blue]"
    )


if __name__ == "__main__":
    app()
