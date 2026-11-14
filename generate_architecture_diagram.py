"""
Generates an ultra-crisp, publication-grade Software Architecture Diagram
for ArchDebt-Lens in PNG format (300 DPI).
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path


def create_architecture_diagram(output_path: str = "archdebt_lens_architecture.png"):
    # High resolution setup (16:10 aspect ratio)
    fig, ax = plt.subplots(figsize=(18, 11), dpi=300)
    fig.patch.set_facecolor("#0F172A")  # Deep slate dark background
    ax.set_facecolor("#0F172A")

    # Coordinate boundaries [0, 100] on X and [0, 100] on Y
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # ------------------ TITLE & HEADER ------------------
    ax.text(
        50, 96.5,
        "ArchDebt-Lens: Software System Architecture",
        fontsize=22, fontweight="bold", color="#38BDF8", ha="center", va="center",
        fontfamily="sans-serif"
    )
    ax.text(
        50, 93.5,
        "Automated Architectural Technical Debt (ATD) Lifecycle Tracking, Dependency Graph Evolution & CI/CD Guardrails",
        fontsize=11.5, color="#94A3B8", ha="center", va="center",
        fontfamily="sans-serif"
    )

    # ------------------ HELPER FUNCTIONS ------------------
    def draw_container(x, y, w, h, title, bg_color="#1E293B", border_color="#334155", title_color="#38BDF8"):
        """Draws a major subsystem container."""
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.5,rounding_size=1.2",
            facecolor=bg_color, edgecolor=border_color, linewidth=1.5,
            zorder=1
        )
        ax.add_patch(rect)
        ax.text(
            x + 1.8, y + h - 2.8,
            title,
            fontsize=11, fontweight="bold", color=title_color, va="center",
            fontfamily="sans-serif", zorder=3
        )

    def draw_card(x, y, w, h, title, items, bg_color="#243248", border_color="#475569", title_color="#F8FAFC", badge=""):
        """Draws an individual component card."""
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.3,rounding_size=0.8",
            facecolor=bg_color, edgecolor=border_color, linewidth=1.2,
            zorder=2
        )
        ax.add_patch(rect)
        
        # Title
        ax.text(
            x + 1.2, y + h - 2.2,
            title,
            fontsize=9.5, fontweight="bold", color=title_color, va="center",
            fontfamily="sans-serif", zorder=3
        )

        # Optional Badge
        if badge:
            badge_box = patches.FancyBboxPatch(
                (x + w - 5.5, y + h - 3.2), 4.8, 1.8,
                boxstyle="round,pad=0.1,rounding_size=0.4",
                facecolor="#0284C7", edgecolor="#38BDF8", linewidth=0.8,
                zorder=3
            )
            ax.add_patch(badge_box)
            ax.text(
                x + w - 3.1, y + h - 2.3,
                badge,
                fontsize=7, fontweight="bold", color="#FFFFFF", ha="center", va="center",
                fontfamily="sans-serif", zorder=4
            )

        # Bullet items
        for i, item in enumerate(items):
            ax.text(
                x + 1.2, y + h - 4.4 - (i * 2.1),
                f"• {item}",
                fontsize=8, color="#CBD5E1", va="center",
                fontfamily="sans-serif", zorder=3
            )

    def draw_arrow(x1, y1, x2, y2, color="#0EA5E9", text="", rad=0.0):
        """Draws an arrow indicating dataflow."""
        arrow = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>,head_length=5,head_width=3",
            linewidth=1.8, color=color,
            zorder=4
        )
        ax.add_patch(arrow)
        if text:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2 + 1.2
            ax.text(
                mid_x, mid_y, text,
                fontsize=7.5, fontweight="bold", color="#E2E8F0",
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#0F172A", edgecolor="#334155", linewidth=0.8),
                zorder=5
            )

    # ------------------ LAYER 1: DATA INGESTION & SOURCES (TOP LEFT) ------------------
    draw_container(4, 69, 44, 21.5, "1. INGESTION & DATA SOURCES", bg_color="#131E33", border_color="#1E3A8A")
    draw_card(6, 71, 19.5, 15.5, "Git Repositories", [
        "Commit trees & histories",
        "Source code diffs & logs",
        "AST-guided git blame",
        "File rename / deletion tracking"
    ], bg_color="#1E293B", badge="VCS")

    draw_card(27, 71, 19.5, 15.5, "Issue Trackers & PRs", [
        "Jira / GitHub Issues (IS)",
        "Pull Request Discussions (PS)",
        "Commit Messages (CM)",
        "Zenodo Replication (14697268)"
    ], bg_color="#1E293B", badge="METADATA")

    # ------------------ LAYER 2: GIT MINING & LIFECYCLE ENGINE (TOP RIGHT) ------------------
    draw_container(52, 69, 44, 21.5, "2. GIT MINING & LIFECYCLE ENGINE (`atd-miner`)", bg_color="#131E33", border_color="#1E3A8A")
    draw_card(54, 71, 19.5, 15.5, "Git History Excavator", [
        "PyDriller / GitPython core",
        "Diff similarity matrices",
        "File modification counter (N_mod)",
        "Historical state sandbox checkout"
    ], bg_color="#1E293B", badge="MINING")

    draw_card(75, 71, 19.5, 15.5, "Lifecycle State Resolver", [
        "Introduction moment tracer",
        "Payment commit linker",
        "Interval duration calculator",
        "Removed files detector (-44.5%)"
    ], bg_color="#1E293B", badge="RESOLVER")

    # Arrow from Layer 1 to Layer 2
    draw_arrow(48, 79, 52, 79, color="#38BDF8", text="Commits & Diffs")

    # ------------------ LAYER 3: STATIC AST & DEPENDENCY GRAPH (MIDDLE) ------------------
    draw_container(4, 40, 92, 25, "3. MULTI-LANGUAGE AST & STATIC GRAPH ENGINE (`atd-graph`)", bg_color="#14233D", border_color="#0369A1")
    
    draw_card(6, 42.5, 27, 18.5, "Multi-Language AST Parser", [
        "Java (Packages, Imports, Invocations)",
        "Python (AST modules, calls, types)",
        "Type reference & hierarchy extractor",
        "Replaces SciTools Understand (Open-Source)"
    ], bg_color="#1E293B", badge="PARSER")

    draw_card(36.5, 42.5, 27, 18.5, "Directed Dependency Graph", [
        "NetworkX DiGraph representation",
        "Symbol & FQN resolution mapping",
        "Class-to-file adjacency models",
        "Circular dependency & cycle detector"
    ], bg_color="#1E293B", badge="GRAPH")

    draw_card(67, 42.5, 27, 18.5, "Structural Metrics Calculator", [
        "FAN-IN (Incoming class connections)",
        "FAN-OUT (Outgoing class dependencies)",
        "SLOC (Source lines of code)",
        "Cyclomatic Complexity (Branch paths)",
        "Normalized: FAN-IN/SLOC & FAN-OUT/SLOC"
    ], bg_color="#1E293B", badge="METRICS")

    # Arrows from Layer 2 to Layer 3
    draw_arrow(63.7, 71, 20, 61, color="#38BDF8", text="Source Trees", rad=-0.1)
    draw_arrow(84.7, 71, 50, 61, color="#38BDF8", text="Lifecycle Diffs", rad=0.1)
    draw_arrow(33, 51.5, 36.5, 51.5, color="#0EA5E9")
    draw_arrow(63.5, 51.5, 67, 51.5, color="#0EA5E9")

    # ------------------ LAYER 4: CLASSIFICATION & STATISTICAL INTELLIGENCE (BOTTOM LEFT) ------------------
    draw_container(4, 9, 44, 27, "4. CLASSIFICATION & STATS (`atd-classifier` & `atd-stats`)", bg_color="#172554", border_color="#1D4ED8")
    
    draw_card(6, 11.5, 19.5, 20.5, "Hybrid ATD Classifier", [
        "NLP SATD keyword detector",
        "Modularity trade-off parser",
        "AST graph diff verifier",
        "Cycle removal confirmation",
        "Eliminates >50% False Positives",
        "True ATD vs Code Debt"
    ], bg_color="#1E293B", badge="HYBRID")

    draw_card(27, 11.5, 19.5, 20.5, "Statistical & Risk Engine", [
        "Anderson-Darling normality",
        "Mann-Whitney U group tests",
        "Cliff's Delta (d) effect sizes",
        "Partial Spearman r (control SLOC)",
        "Debt Paradox Centralization Risk",
        "Flags +57.5% FAN-IN spikes"
    ], bg_color="#1E293B", badge="STATISTICS")

    # Arrow from Layer 3 to Layer 4
    draw_arrow(48, 42.5, 26, 36, color="#38BDF8", text="Graph Metrics", rad=0.1)

    # ------------------ LAYER 5: INTERFACES & CI/CD GUARDRAILS (BOTTOM RIGHT) ------------------
    draw_container(52, 9, 44, 27, "5. DELIVERY, CI/CD GUARDRAILS & INTERFACES", bg_color="#112A36", border_color="#0F766E")
    
    draw_card(54, 11.5, 19.5, 20.5, "Developer CLI & CI/CD Bot", [
        "Typer CLI (atd-lens scan/trace)",
        "GitHub Action PR Guardrail",
        "Automated PR review comments",
        "Centralization threshold alerts",
        "Decoupling pattern remedies",
        "(Facade, ISP, Mediator)"
    ], bg_color="#1E293B", badge="GUARDRAIL")

    draw_card(75, 11.5, 19.5, 20.5, "Interactive UI & Reports", [
        "D3.js force-directed graph",
        "Code Avoidance scatter matrix",
        "(Complexity vs. Changes)",
        "Standalone HTML audit reports",
        "Empirical Markdown generator",
        "PDF Executive summary report"
    ], bg_color="#1E293B", badge="VISUALS")

    # Arrow from Layer 4 to Layer 5
    draw_arrow(48, 22, 52, 22, color="#2DD4BF", text="Risks & Predictions")

    # ------------------ FOOTER INFO BAR ------------------
    footer_box = patches.FancyBboxPatch(
        (4, 2.2), 92, 4.8,
        boxstyle="round,pad=0.3,rounding_size=0.6",
        facecolor="#1E293B", edgecolor="#334155", linewidth=1.0,
        zorder=2
    )
    ax.add_patch(footer_box)

    ax.text(
        6, 4.6,
        "CORE CAPABILITIES:",
        fontsize=8.5, fontweight="bold", color="#38BDF8", va="center",
        fontfamily="sans-serif", zorder=3
    )
    ax.text(
        22, 4.6,
        "1. Git-Native Lifecycle Tracing  |  2. Open-Source Multi-Language AST  |  3. Hybrid ATD Detection  |  4. Debt Paradox Prevention  |  5. 100% Paper Verified",
        fontsize=8, color="#E2E8F0", va="center",
        fontfamily="sans-serif", zorder=3
    )

    plt.tight_layout()
    out_file = Path(output_path).resolve()
    plt.savefig(str(out_file), format="png", dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    return str(out_file)


if __name__ == "__main__":
    out = create_architecture_diagram()
    print(f"Architecture diagram generated successfully: {out}")
