"""
Debt Paradox & Centralization Risk Evaluator.
Detects when ATD repayment increases class centralization and coupling.
"""

from typing import Dict, List, Optional
from archdebt_lens.models.schemas import CentralizationRisk, FileMetricRecord


class DebtParadoxEvaluator:
    """Evaluates the risk of architectural centralization during ATD repayment."""

    @staticmethod
    def evaluate_class_risk(
        class_name: str,
        intro_metric: Optional[FileMetricRecord],
        payment_metric: Optional[FileMetricRecord],
        fan_in_threshold_percent: float = 50.0,
    ) -> CentralizationRisk:
        """
        Evaluates whether a surviving class has undergone dangerous centralization.
        """
        intro_fi = intro_metric.fan_in if intro_metric else 0
        pay_fi = payment_metric.fan_in if payment_metric else 0

        intro_fo = intro_metric.fan_out if intro_metric else 0
        pay_fo = payment_metric.fan_out if payment_metric else 0

        if pay_fi >= intro_fi:
            fi_delta_pct = ((pay_fi - intro_fi) / max(1, intro_fi)) * 100.0
        else:
            fi_delta_pct = -(((intro_fi - pay_fi) / max(1, intro_fi)) * 100.0)

        if pay_fo >= intro_fo:
            fo_delta_pct = ((pay_fo - intro_fo) / max(1, intro_fo)) * 100.0
        else:
            fo_delta_pct = -(((intro_fo - pay_fo) / max(1, intro_fo)) * 100.0)

        # Detect centralization spike
        is_paradox = pay_fi > intro_fi and fi_delta_pct >= fan_in_threshold_percent

        if is_paradox and pay_fi > 50:
            risk_level = "CRITICAL"
            recom = (
                f"Class '{class_name}' experienced a +{fi_delta_pct:.1f}% FAN-IN spike "
                f"(now {pay_fi} dependents). High risk of single point of failure. "
                "Recommend decomposing via Facade or Mediator pattern."
            )
        elif is_paradox:
            risk_level = "HIGH"
            recom = (
                f"Class '{class_name}' centralized incoming dependencies (+{fi_delta_pct:.1f}%). "
                "Consider applying Interface Segregation (ISP) or event-driven decoupling."
            )
        elif pay_fi > intro_fi:
            risk_level = "MEDIUM"
            recom = "Moderate dependency increase. Monitor in future PRs."
        else:
            risk_level = "LOW"
            recom = "Healthy dependency evolution; no centralization spike detected."

        return CentralizationRisk(
            target_class=class_name,
            intro_fan_in=intro_fi,
            payment_fan_in=pay_fi,
            fan_in_growth_percent=round(fi_delta_pct, 2),
            intro_fan_out=intro_fo,
            payment_fan_out=pay_fo,
            fan_out_growth_percent=round(fo_delta_pct, 2),
            is_paradox_risk=is_paradox,
            risk_level=risk_level,
            recommendation=recom,
        )

    @classmethod
    def evaluate_all(
        cls,
        intro_metrics: Dict[str, FileMetricRecord],
        payment_metrics: Dict[str, FileMetricRecord],
        fan_in_threshold_percent: float = 50.0,
    ) -> List[CentralizationRisk]:
        """Evaluates all classes present in the payment phase."""
        risks: List[CentralizationRisk] = []
        for file_path, pay_rec in payment_metrics.items():
            intro_rec = intro_metrics.get(file_path)
            risk = cls.evaluate_class_risk(
                file_path, intro_rec, pay_rec, fan_in_threshold_percent
            )
            risks.append(risk)
        return sorted(
            risks,
            key=lambda r: (r.is_paradox_risk, r.fan_in_growth_percent),
            reverse=True,
        )
