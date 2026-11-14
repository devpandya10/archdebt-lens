"""
CI/CD Pull Request Guardrail & Architectural Reviewer.
Inspects PRs for dependency centralization spikes, modularity violations, and the Debt Paradox.
"""

from typing import Dict, List, Optional
from archdebt_lens.classifier.hybrid import HybridATDClassifier
from archdebt_lens.graph.dependency import DependencyGraphBuilder
from archdebt_lens.graph.metrics import MetricsCalculator
from archdebt_lens.models.schemas import CentralizationRisk, LifecycleStage
from archdebt_lens.stats.paradox_risk import DebtParadoxEvaluator


class PRCheckResult:
    def __init__(
        self,
        is_passed: bool,
        classification_category: str,
        confidence: float,
        centralization_risks: List[CentralizationRisk],
        summary_markdown: str,
    ):
        self.is_passed = is_passed
        self.classification_category = classification_category
        self.confidence = confidence
        self.centralization_risks = centralization_risks
        self.summary_markdown = summary_markdown


class PRGuardrailChecker:
    """Evaluates pull requests to prevent harmful architectural centralization."""

    def __init__(self, fan_in_threshold_pct: float = 50.0):
        self.fan_in_threshold_pct = fan_in_threshold_pct
        self.classifier = HybridATDClassifier()

    def evaluate_pr(
        self,
        pr_title: str,
        pr_description: str,
        files_before: Dict[str, str],
        files_after: Dict[str, str],
    ) -> PRCheckResult:
        """
        Evaluates a PR given code before and after the change.
        """
        # Build graph before
        g_before = DependencyGraphBuilder()
        for path, content in files_before.items():
            g_before.add_file(path, content)
        g_before.build_edges()

        # Build graph after
        g_after = DependencyGraphBuilder()
        for path, content in files_after.items():
            g_after.add_file(path, content)
        g_after.build_edges()

        affected_files = list(set(files_before.keys()).union(files_after.keys()))

        # 1. Hybrid classification
        full_text = f"{pr_title}\n{pr_description}"
        cls_result = self.classifier.classify(
            text_content=full_text,
            builder_before=g_before,
            builder_after=g_after,
            affected_files=affected_files,
        )

        # 2. Compute metrics before and after
        metrics_before = MetricsCalculator.calculate_all_metrics(
            g_before, commit_hash="BASE", stage=LifecycleStage.INTRODUCTION
        )
        metrics_after = MetricsCalculator.calculate_all_metrics(
            g_after, commit_hash="HEAD", stage=LifecycleStage.PAYMENT
        )

        # 3. Evaluate Debt Paradox / Centralization risks
        risks = DebtParadoxEvaluator.evaluate_all(
            metrics_before, metrics_after, self.fan_in_threshold_pct
        )

        critical_risks = [r for r in risks if r.risk_level == "CRITICAL"]

        # PR fails if there are CRITICAL centralization risks
        is_passed = len(critical_risks) == 0

        # 4. Generate GitHub-style Markdown comment
        md = self._generate_markdown_report(
            pr_title, cls_result, risks, is_passed
        )

        return PRCheckResult(
            is_passed=is_passed,
            classification_category=cls_result.predicted_category,
            confidence=cls_result.confidence,
            centralization_risks=risks,
            summary_markdown=md,
        )

    def _generate_markdown_report(
        self, pr_title: str, cls_result, risks: List[CentralizationRisk], is_passed: bool
    ) -> str:
        status_icon = (
            "✅ **PASSED**" if is_passed
            else "⚠️ **ACTION REQUIRED: Centralization Risk Detected**"
        )

        md_lines = [
            f"## {status_icon} - ArchDebt-Lens Review",
            f"**PR Assessment:** `{cls_result.predicted_category}` "
            f"(Confidence: {cls_result.confidence * 100:.1f}%)",
            "",
            "### Architectural Impact Analysis",
        ]

        if cls_result.explanation:
            for exp in cls_result.explanation:
                md_lines.append(f"- {exp}")
            md_lines.append("")

        flagged_risks = [r for r in risks if r.is_paradox_risk]
        if flagged_risks:
            md_lines.append("### 🚨 Centralization Bottlenecks (Debt Paradox)")
            md_lines.append(
                "| Target Class | Intro FAN-IN | Payment FAN-IN | Growth | Severity | Recommendation |"
            )
            md_lines.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
            for r in flagged_risks:
                md_lines.append(
                    f"| `{r.target_class}` | {r.intro_fan_in} | {r.payment_fan_in} | "
                    f"+{r.fan_in_growth_percent:.1f}% | **{r.risk_level}** | {r.recommendation} |"
                )
            md_lines.append("")
        else:
            md_lines.append("✅ No excessive class centralization detected across the PR.")
            md_lines.append("")

        md_lines.append("> *Powered by ArchDebt-Lens: Automated Architectural Technical Debt Intelligence*")
        return "\n".join(md_lines)
