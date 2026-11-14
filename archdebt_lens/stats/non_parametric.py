"""
Non-parametric statistical tests and effect size calculations.
Includes Mann-Whitney U test, Cliff's Delta, and Anderson-Darling normality tests.
"""

from typing import Dict, List, Tuple
import numpy as np
from scipy import stats


def check_normality_anderson(data: List[float]) -> Tuple[bool, float, float]:
    """
    Performs Anderson-Darling test for normality.
    Returns (is_normal, statistic, critical_value_5pct).
    """
    if len(data) < 5:
        return False, 0.0, 0.0
    res = stats.anderson(data, dist="norm")
    crit_5 = res.critical_values[2]  # index 2 corresponds to 5% significance
    is_normal = bool(res.statistic < crit_5)
    return is_normal, float(res.statistic), float(crit_5)


def calculate_mann_whitney_u(
    sample_intro: List[float], sample_payment: List[float], alternative: str = "two-sided"
) -> Tuple[float, float, bool]:
    """
    Computes Mann-Whitney U test between introduction and payment phases.
    Returns (statistic, p_value, is_significant_at_005).
    """
    if not sample_intro or not sample_payment:
        return 0.0, 1.0, False

    stat, p_val = stats.mannwhitneyu(sample_payment, sample_intro, alternative=alternative)
    return float(stat), float(p_val), bool(p_val < 0.05)


def calculate_cliffs_delta(sample1: List[float], sample2: List[float]) -> Tuple[float, str]:
    """
    Computes Cliff's Delta (d) non-parametric effect size between sample1 and sample2.
    Thresholds:
      |d| < 0.147: negligible
      0.147 <= |d| < 0.33: small
      0.33 <= |d| < 0.474: medium
      |d| >= 0.474: large
    """
    n1 = len(sample1)
    n2 = len(sample2)
    if n1 == 0 or n2 == 0:
        return 0.0, "negligible"

    # Compute dominance count
    arr1 = np.array(sample1)
    arr2 = np.array(sample2)

    greater = np.sum(arr1[:, None] > arr2)
    lesser = np.sum(arr1[:, None] < arr2)

    delta = float((greater - lesser) / (n1 * n2))
    abs_delta = abs(delta)

    if abs_delta < 0.147:
        magnitude = "negligible"
    elif abs_delta < 0.33:
        magnitude = "small"
    elif abs_delta < 0.474:
        magnitude = "medium"
    else:
        magnitude = "large"

    return round(delta, 4), magnitude
