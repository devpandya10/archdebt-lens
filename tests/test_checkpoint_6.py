"""Unit tests for Checkpoint 6: Developer CLI & CI/CD Guardrail."""

from typer.testing import CliRunner
import pytest
from archdebt_lens.cli.main import app
from archdebt_lens.guardrail.pr_checker import PRGuardrailChecker

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "ArchDebt-Lens" in result.stdout
    assert "Sutoyo et al." in result.stdout


def test_cli_scan(tmp_path):
    # Create sample files
    f1 = tmp_path / "Service.java"
    f1.write_text("public class Service {}")
    f2 = tmp_path / "Client.java"
    f2.write_text("import Service; public class Client { private Service s; }")

    result = runner.invoke(app, ["scan", "--path", str(tmp_path), "--ext", ".java"])
    assert result.exit_code == 0
    assert "Service.java" in result.stdout
    assert "Client.java" in result.stdout


def test_pr_guardrail_paradox_flag():
    checker = PRGuardrailChecker(fan_in_threshold_pct=50.0)

    # Before: Endpoint has 1 incoming connection
    before_files = {
        "Endpoint.java": "public class Endpoint {}",
        "ClientA.java": "import Endpoint; public class ClientA { private Endpoint e; }",
    }

    # After: Endpoint gets 4 new incoming connections (+300% increase)
    after_files = {
        "Endpoint.java": "public class Endpoint {}",
        "ClientA.java": "import Endpoint; public class ClientA { private Endpoint e; }",
        "ClientB.java": "import Endpoint; public class ClientB { private Endpoint e; }",
        "ClientC.java": "import Endpoint; public class ClientC { private Endpoint e; }",
        "ClientD.java": "import Endpoint; public class ClientD { private Endpoint e; }",
    }

    result = checker.evaluate_pr(
        pr_title="Refactor Endpoint architecture",
        pr_description="Resolves modularity issue by routing all clients through Endpoint",
        files_before=before_files,
        files_after=after_files,
    )

    # Verify that centralization spike was detected
    assert len(result.centralization_risks) > 0
    endpoint_risk = next(r for r in result.centralization_risks if "Endpoint.java" in r.target_class)
    assert endpoint_risk.is_paradox_risk is True
    assert endpoint_risk.fan_in_growth_percent >= 100.0
    assert "Centralization Bottlenecks" in result.summary_markdown
