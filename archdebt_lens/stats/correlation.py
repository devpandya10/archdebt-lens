"""
Partial Spearman Rank Correlation analysis controlling for confounding variables (SLOC).
Automates the statistical methodology of RQ2 in Sutoyo et al. (2025).
"""

import math
from typing import List, Tuple
import numpy as np
from scipy import stats


def partial_spearman_correlation(
    x: List[float], y: List[float], z_control: List[float]
) -> Tuple[float, float, Tuple[float, float]]:
    """
    Computes Partial Spearman's correlation coefficient r(x, y | z),
    controlling for z (SLOC).
    Returns (r, p_value, (ci_lower, ci_upper)).
    """
    n = len(x)
    if n < 5:
        return 0.0, 1.0, (-1.0, 1.0)

    # Rank-transform variables
    rx = stats.rankdata(x)
    ry = stats.rankdata(y)
    rz = stats.rankdata(z_control)

    # Pairwise Pearson correlations on ranks (= Spearman r)
    r_xy, _ = stats.pearsonr(rx, ry)
    r_xz, _ = stats.pearsonr(rx, rz)
    r_yz, _ = stats.pearsonr(ry, rz)

    denom = math.sqrt(max(1e-12, (1.0 - r_xz**2) * (1.0 - r_yz**2)))
    r_xyz = (r_xy - (r_xz * r_yz)) / denom
    r_xyz = max(-1.0, min(1.0, r_xyz))

    # Degrees of freedom: n - 2 - k (k=1 control variable)
    df = n - 3
    if df <= 0 or abs(r_xyz) >= 1.0:
        p_val = 0.0 if abs(r_xyz) >= 1.0 else 1.0
        return round(r_xyz, 3), p_val, (-1.0, 1.0)

    # t-statistic for hypothesis testing
    t_stat = r_xyz * math.sqrt(df / (1.0 - r_xyz**2))
    p_val = 2.0 * (1.0 - stats.t.cdf(abs(t_stat), df=df))

    # 95% CI using Fisher z-transformation
    z = np.arctanh(r_xyz)
    se = 1.0 / math.sqrt(n - 4) if n > 4 else 1.0
    z_low = z - 1.96 * se
    z_high = z + 1.96 * se
    ci_low = float(np.tanh(z_low))
    ci_high = float(np.tanh(z_high))

    return round(r_xyz, 3), float(p_val), (round(ci_low, 2), round(ci_high, 2))
