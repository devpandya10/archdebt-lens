"""Unit tests for Checkpoint 7: Interactive HTML Report Generator."""

from pathlib import Path
import pytest
from archdebt_lens.graph.dependency import DependencyGraphBuilder
from archdebt_lens.graph.metrics import MetricsCalculator
from archdebt_lens.ui.report_generator import HTMLReportGenerator


def test_html_report_generation(tmp_path):
    builder = DependencyGraphBuilder()
    builder.add_file("Endpoint.java", "public class Endpoint {}")
    builder.add_file("SendProcessor.java", "import Endpoint; public class SendProcessor { private Endpoint ep; }")
    builder.build_edges()

    metrics = MetricsCalculator.calculate_all_metrics(builder)
    report_file = tmp_path / "test_report.html"

    out_path = HTMLReportGenerator.generate_report(
        title="Apache Camel ATD #1 Report",
        metrics=metrics,
        builder=builder,
        output_path=str(report_file)
    )

    assert Path(out_path).exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Apache Camel ATD #1 Report" in content
    assert "d3.v7.min.js" in content
    assert "Endpoint.java" in content
    assert "SendProcessor.java" in content
    assert "graphData" in content
