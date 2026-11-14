"""
Interactive HTML Report Generator for ArchDebt-Lens.
Renders self-contained D3.js force-directed graphs and Code Avoidance scatter matrices.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from archdebt_lens.graph.dependency import DependencyGraphBuilder
from archdebt_lens.graph.metrics import MetricsCalculator
from archdebt_lens.models.schemas import CentralizationRisk, FileMetricRecord


class HTMLReportGenerator:
    """Generates an interactive, standalone HTML architectural report."""

    @staticmethod
    def generate_report(
        title: str,
        metrics: Dict[str, FileMetricRecord],
        builder: Optional[DependencyGraphBuilder] = None,
        risks: Optional[List[CentralizationRisk]] = None,
        output_path: str = "archdebt_report.html",
    ) -> str:
        summary = MetricsCalculator.calculate_summary_stats(metrics)
        risks = risks or []

        # Prepare Graph Nodes and Edges for D3.js
        nodes = []
        node_id_map = {}
        for idx, (path, m) in enumerate(metrics.items()):
            node_id_map[path] = idx
            nodes.append({
                "id": idx,
                "name": Path(path).name,
                "path": path,
                "fan_in": m.fan_in,
                "fan_out": m.fan_out,
                "sloc": m.sloc,
                "complexity": m.cyclomatic_complexity,
                "changes": m.modification_count,
            })

        edges = []
        if builder:
            for u, v in builder.graph.edges:
                if u in node_id_map and v in node_id_map:
                    edges.append({
                        "source": node_id_map[u],
                        "target": node_id_map[v],
                    })

        graph_data_json = json.dumps({"nodes": nodes, "links": edges})

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - ArchDebt-Lens Report</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0; padding: 24px; background: #0f172a; color: #f8fafc;
    }}
    .header {{
      display: flex; justify-content: space-between; align-items: center;
      border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px;
    }}
    .title {{ font-size: 26px; font-weight: 700; color: #38bdf8; }}
    .badge {{
      background: #0284c7; color: white; padding: 4px 12px;
      border-radius: 9999px; font-size: 13px; font-weight: 600;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .card {{ background: #1e293b; padding: 18px; border-radius: 12px; border: 1px solid #334155; }}
    .card-num {{ font-size: 32px; font-weight: 800; color: #38bdf8; margin-top: 6px; }}
    .card-label {{ font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; }}
    .view-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
    .panel {{ background: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 16px; }}
    .panel-title {{ font-size: 16px; font-weight: 600; margin-bottom: 12px; color: #e2e8f0; }}
    svg {{ width: 100%; height: 420px; background: #090d16; border-radius: 8px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }}
    th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #334155; }}
    th {{ background: #0f172a; color: #94a3b8; font-weight: 600; }}
    tr:hover {{ background: #243248; }}
    .danger {{ color: #f87171; font-weight: 600; }}
    .success {{ color: #4ade80; }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="title">{title}</div>
      <div style="color: #94a3b8; margin-top: 4px;">Automated Architectural Technical Debt Assessment</div>
    </div>
    <span class="badge">ArchDebt-Lens v1.0</span>
  </div>

  <div class="cards">
    <div class="card">
      <div class="card-label">Total Files Analyzed</div>
      <div class="card-num">{int(summary['file_count'])}</div>
    </div>
    <div class="card">
      <div class="card-label">Average FAN-IN</div>
      <div class="card-num">{summary['fan_in_avg']:.2f}</div>
    </div>
    <div class="card">
      <div class="card-label">Max Class FAN-IN</div>
      <div class="card-num">{summary['fan_in_max']:.0f}</div>
    </div>
    <div class="card">
      <div class="card-label">Average FAN-OUT</div>
      <div class="card-num">{summary['fan_out_avg']:.2f}</div>
    </div>
  </div>

  <div class="view-container">
    <div class="panel">
      <div class="panel-title">🌐 Architectural Dependency Graph (Force-Directed)</div>
      <div id="graph-container"></div>
    </div>
    <div class="panel">
      <div class="panel-title">📉 Code Avoidance Matrix (Complexity vs. Changes)</div>
      <div id="scatter-container"></div>
    </div>
  </div>

  <div class="panel">
    <div class="panel-title">📁 High-Dependency Architectural Modules</div>
    <table>
      <thead>
        <tr>
          <th>File Path</th>
          <th>FAN-IN</th>
          <th>FAN-OUT</th>
          <th>SLOC</th>
          <th>Complexity</th>
          <th>Modifications</th>
        </tr>
      </thead>
      <tbody>
"""
        for path, m in sorted(metrics.items(), key=lambda x: x[1].fan_in, reverse=True)[:15]:
            html_template += f"""
        <tr>
          <td><code>{path}</code></td>
          <td class="success"><b>{m.fan_in}</b></td>
          <td>{m.fan_out}</td>
          <td>{m.sloc}</td>
          <td>{m.cyclomatic_complexity:.1f}</td>
          <td>{m.modification_count}</td>
        </tr>
"""

        html_template += f"""
      </tbody>
    </table>
  </div>

  <script>
    const graphData = {graph_data_json};

    // Render D3 Force-Directed Graph
    const width = 600, height = 420;
    const svg = d3.select("#graph-container")
      .append("svg")
      .attr("viewBox", [0, 0, width, height]);

    const simulation = d3.forceSimulation(graphData.nodes)
      .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(60))
      .force("charge", d3.forceManyBody().strength(-120))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
      .attr("stroke", "#475569")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(graphData.links)
      .join("line")
      .attr("stroke-width", 1.5);

    const node = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .selectAll("circle")
      .data(graphData.nodes)
      .join("circle")
      .attr("r", d => Math.max(5, Math.min(22, 5 + d.fan_in * 1.5)))
      .attr("fill", d => d.fan_in > 10 ? "#ef4444" : "#38bdf8")
      .call(d3.drag()
        .on("start", (e, d) => {{ if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
        .on("drag", (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
        .on("end", (e, d) => {{ if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}));

    node.append("title").text(d => `${{d.name}}\\nFAN-IN: ${{d.fan_in}}\\nFAN-OUT: ${{d.fan_out}}`);

    simulation.on("tick", () => {{
      link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
      node.attr("cx", d => d.x).attr("cy", d => d.y);
    }});

    // Render Scatter Plot: Complexity vs Changes
    const scatterSvg = d3.select("#scatter-container")
      .append("svg")
      .attr("viewBox", [0, 0, width, height]);

    const margin = {{top: 20, right: 20, bottom: 40, left: 50}};
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    const xMax = d3.max(graphData.nodes, d => d.complexity) || 20;
    const yMax = d3.max(graphData.nodes, d => d.changes) || 20;

    const x = d3.scaleLinear().domain([0, xMax * 1.1]).range([0, innerW]);
    const y = d3.scaleLinear().domain([0, yMax * 1.1]).range([innerH, 0]);

    const g = scatterSvg.append("g").attr("transform", `translate(${{margin.left}},${{margin.top}})`);
    g.append("g").attr("transform", `translate(0,${{innerH}})`).call(d3.axisBottom(x)).attr("color", "#94a3b8");
    g.append("g").call(d3.axisLeft(y)).attr("color", "#94a3b8");

    g.selectAll("dot")
      .data(graphData.nodes)
      .join("circle")
      .attr("cx", d => x(d.complexity))
      .attr("cy", d => y(d.changes))
      .attr("r", d => Math.max(4, Math.min(16, 4 + d.fan_in)))
      .style("fill", "#f59e0b")
      .style("opacity", 0.8)
      .append("title")
      .text(d => `${{d.name}}\\nComplexity: ${{d.complexity}}\\nChanges: ${{d.changes}}`);
  </script>
</body>
</html>
"""
        out_file = Path(output_path)
        out_file.write_text(html_template, encoding="utf-8")
        return str(out_file.resolve())
