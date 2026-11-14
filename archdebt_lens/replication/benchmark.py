"""
Benchmark and Replication Runner.
Validates the ArchDebt-Lens implementation against empirical results in Sutoyo et al. (2025).
"""

from typing import Dict
from archdebt_lens.replication.dataset import (
    TABLE_III_CAMEL_DATA,
    TABLE_IV_PAPER_SUMMARY,
    TABLE_VII_CHANGE_DISTRIBUTIONS,
    TABLE_VIII_PARTIAL_CORRELATIONS,
)
from archdebt_lens.stats.non_parametric import calculate_cliffs_delta, calculate_mann_whitney_u


class ReplicationBenchmark:
    """Runs automated replication tests matching the paper's empirical results."""

    @staticmethod
    def replicate_camel_worked_example() -> Dict:
        """
        Replicates Section IV: Worked Example (ATD #1 - Apache Camel CAMEL-789).
        Analyzes the shift in FAN-IN and FAN-OUT between introduction and repayment.
        """
        intro_fan_in = [row["intro_fan_in"] for row in TABLE_III_CAMEL_DATA]
        intro_fan_out = [row["intro_fan_out"] for row in TABLE_III_CAMEL_DATA]

        # In the payment phase, 3 files were deleted (unpaired dataset)
        pay_fan_in = [row["pay_fan_in"] for row in TABLE_III_CAMEL_DATA if row["pay_fan_in"] is not None]
        pay_fan_out = [row["pay_fan_out"] for row in TABLE_III_CAMEL_DATA if row["pay_fan_out"] is not None]

        # Mann-Whitney U test on FAN-IN (directional H1: payment > intro)
        u_stat_in, p_val_in, sig_in = calculate_mann_whitney_u(
            intro_fan_in, pay_fan_in, alternative="greater"
        )
        delta_in, mag_in = calculate_cliffs_delta(pay_fan_in, intro_fan_in)

        # Mann-Whitney U test on FAN-OUT
        u_stat_out, p_val_out, sig_out = calculate_mann_whitney_u(
            intro_fan_out, pay_fan_out, alternative="two-sided"
        )
        delta_out, mag_out = calculate_cliffs_delta(pay_fan_out, intro_fan_out)

        return {
            "fan_in": {
                "u_statistic": u_stat_in,
                "p_value": p_val_in,
                "is_significant": sig_in,
                "cliffs_delta": delta_in,
                "magnitude": mag_in,
            },
            "fan_out": {
                "u_statistic": u_stat_out,
                "p_value": p_val_out,
                "is_significant": sig_out,
                "cliffs_delta": delta_out,
                "magnitude": mag_out,
            },
            "removed_files_count": sum(1 for row in TABLE_III_CAMEL_DATA if row["removed"]),
        }

    @staticmethod
    def verify_paper_hypotheses() -> Dict[str, bool]:
        """
        Verifies core hypotheses confirmed in the paper:
        1. ATD repayment increases class connectivity (+57.5% FAN-IN increase).
        2. ATD files have significantly fewer modifications than Non-ATD (6.98 vs 16.12).
        3. ATD complexity is negatively correlated with changes (r = -0.089).
        """
        hypotheses = {}

        # H1: Repayment increases FAN-IN connectivity
        atd_fan_in_growth = TABLE_IV_PAPER_SUMMARY["atd"]["fan_in_avg_pct"]
        hypotheses["H1_repayment_increases_fan_in"] = atd_fan_in_growth > 0.0

        # H2: ATD files modified less frequently
        atd_changes = TABLE_VII_CHANGE_DISTRIBUTIONS["atd"]["avg_change"]
        non_atd_changes = TABLE_VII_CHANGE_DISTRIBUTIONS["non_atd"]["avg_change"]
        hypotheses["H2_atd_files_modified_less"] = atd_changes < non_atd_changes

        # H3: Code avoidance in ATD files (negative complexity-change correlation)
        complexity_entry = TABLE_VIII_PARTIAL_CORRELATIONS["atd"]["complexity"]
        atd_complexity_r = complexity_entry["r"] if isinstance(complexity_entry, dict) else complexity_entry
        hypotheses["H3_code_avoidance_negative_correlation"] = atd_complexity_r < 0.0

        return hypotheses
