"""Unit tests for Checkpoint 3: Multi-Language AST & Dependency Graph Engine."""

import pytest
from archdebt_lens.graph.parser import SourceCodeParser
from archdebt_lens.graph.dependency import DependencyGraphBuilder
from archdebt_lens.graph.metrics import MetricsCalculator
from archdebt_lens.models.schemas import LifecycleStage


def test_java_parser():
    code = """
    package org.apache.camel;

    import org.apache.camel.processor.SendProcessor;
    import java.util.List;

    // Class comment
    public class Endpoint {
        private SendProcessor processor;

        public void process(int x) {
            if (x > 0 && x < 100) {
                System.out.println("Valid");
            } else {
                for (int i = 0; i < x; i++) {
                    System.out.println(i);
                }
            }
        }
    }
    """
    entity = SourceCodeParser.parse_java("Endpoint.java", code)
    assert entity.package_name == "org.apache.camel"
    assert "Endpoint" in entity.declared_classes
    assert "org.apache.camel.processor.SendProcessor" in entity.imports
    assert "SendProcessor" in entity.referenced_types
    assert entity.sloc > 10
    assert entity.cyclomatic_complexity >= 4  # if, &&, for, + base 1


def test_dependency_graph_connectivity():
    builder = DependencyGraphBuilder()

    endpoint_code = """
    package org.apache.camel;
    public class Endpoint {
        public void connect() {}
    }
    """

    processor_code = """
    package org.apache.camel.processor;
    import org.apache.camel.Endpoint;

    public class SendProcessor {
        private Endpoint endpoint;
        public void send() {
            endpoint.connect();
        }
    }
    """

    builder.add_file("Endpoint.java", endpoint_code)
    builder.add_file("SendProcessor.java", processor_code)
    builder.build_edges()

    # SendProcessor depends on Endpoint:
    # Endpoint has FAN-IN = 1, FAN-OUT = 0
    # SendProcessor has FAN-IN = 0, FAN-OUT = 1
    assert builder.get_fan_in("Endpoint.java") == 1
    assert builder.get_fan_out("Endpoint.java") == 0
    assert builder.get_fan_in("SendProcessor.java") == 0
    assert builder.get_fan_out("SendProcessor.java") == 1


def test_metrics_calculator():
    builder = DependencyGraphBuilder()

    builder.add_file("A.java", "public class A { public void foo() {} }")
    builder.add_file("B.java", "import A; public class B { private A a; }")
    builder.build_edges()

    metric_a = MetricsCalculator.calculate_file_metrics(
        builder, "A.java", commit_hash="c1", stage=LifecycleStage.PAYMENT, modification_count=3
    )

    assert metric_a.fan_in == 1
    assert metric_a.fan_out == 0
    assert metric_a.modification_count == 3
    assert metric_a.fan_in_per_sloc > 0.0

    summary = MetricsCalculator.calculate_summary_stats(
        {"A.java": metric_a}
    )
    assert summary["file_count"] == 1.0
    assert summary["fan_in_avg"] == 1.0
