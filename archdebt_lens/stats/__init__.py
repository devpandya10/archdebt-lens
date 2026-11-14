"""Non-parametric statistics, partial correlation, and debt paradox evaluation."""

from archdebt_lens.stats.correlation import partial_spearman_correlation
from archdebt_lens.stats.non_parametric import (
    calculate_cliffs_delta,
    calculate_mann_whitney_u,
    check_normality_anderson,
)
from archdebt_lens.stats.paradox_risk import DebtParadoxEvaluator

__all__ = [
    "partial_spearman_correlation",
    "calculate_cliffs_delta",
    "calculate_mann_whitney_u",
    "check_normality_anderson",
    "DebtParadoxEvaluator",
]
