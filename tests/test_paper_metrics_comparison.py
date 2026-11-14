"""
Unit tests validating exact replication of metrics and tables published in
"Tracing the Lifecycle of Architecture Technical Debt in Software Systems: A Dependency Approach"
(Sutoyo, Avgeriou, & Capiluppi, 2025).
"""

import pytest
from archdebt_lens.replication.compare_paper import PaperMetricsComparator
from archdebt_lens.replication.dataset import (
    TABLE_III_CAMEL_DATA,
    TABLE_IV_PAPER_SUMMARY,
    TABLE_V_ATD_ITEMS,
    TABLE_VI_NON_ATD_ITEMS,
    TABLE_VII_CHANGE_DISTRIBUTIONS,
    TABLE_VIII_PARTIAL_CORRELATIONS,
    WORKED_EXAMPLE_ATD1_STATS,
)


def test_table_iii_camel_atd1_replication():
    """Validates Table III Apache Camel CAMEL-789 data and removal of builder classes."""
    comparator = PaperMetricsComparator()
    comps = comparator.compare_worked_example_atd1()

    for c in comps:
        assert c["match"] is True, f"Mismatch in {c['metric']}: {c['computed_val']} vs {c['paper_val']}"

    # Specifically check Endpoint.java vs ChoiceBuilder.java
    endpoint = next(r for r in TABLE_III_CAMEL_DATA if "Endpoint.java" in r["filename"])
    choice = next(r for r in TABLE_III_CAMEL_DATA if "ChoiceBuilder.java" in r["filename"])

    assert endpoint["intro_fan_in"] == 11
    assert endpoint["pay_fan_in"] == 196
    assert choice["removed"] is True
    assert choice["pay_fan_in"] is None


def test_table_iv_overall_metric_changes():
    """Validates Table IV: FAN-IN, FAN-OUT shifts and Cliff's Delta effect sizes."""
    comparator = PaperMetricsComparator()
    comps = comparator.compare_table_iv_summary()

    for c in comps:
        assert c["match"] is True, f"Mismatch in {c['metric']}: {c['computed_val']} vs {c['paper_val']}"

    atd = TABLE_IV_PAPER_SUMMARY["atd"]
    non_atd = TABLE_IV_PAPER_SUMMARY["non_atd"]

    # ATD repayment increased FAN-IN by 57.5% and FAN-OUT by 26.7%
    assert atd["fan_in_avg_pct"] == 57.5
    assert atd["fan_out_avg_pct"] == 26.7
    assert atd["file_reduction_pct"] == -44.5
    assert atd["fan_in_delta_magnitude"] == "negligible"

    # Non-ATD increased FAN-IN by 89.06% and FAN-OUT by 36.18%
    assert non_atd["fan_in_avg_pct"] == 89.06
    assert non_atd["fan_out_avg_pct"] == 36.18
    assert non_atd["fan_in_delta_magnitude"] == "small"


def test_table_v_and_vi_significance_indicators():
    """Validates Table V & VI: Item-by-item significance pattern."""
    # In Table V, items with significant FAN-IN differences were #1, #10, #11, #16, #17
    sig_fan_in_items = [
        k for k, v in TABLE_V_ATD_ITEMS.items() if v["fan_in"][0] == "Y"
    ]
    assert "ATD #1" in sig_fan_in_items
    assert "ATD #10" in sig_fan_in_items
    assert "ATD #11" in sig_fan_in_items
    assert "ATD #16" in sig_fan_in_items
    assert "ATD #17" in sig_fan_in_items

    # Items #3 and #6 were folders only ("-", "-")
    assert TABLE_V_ATD_ITEMS["ATD #3"]["fan_in"] == ("-", "-")
    assert TABLE_V_ATD_ITEMS["ATD #6"]["fan_in"] == ("-", "-")

    # In Table VI, only Non-ATD #14 and #15 had significant differences
    sig_non_atd = [
        k for k, v in TABLE_VI_NON_ATD_ITEMS.items() if v["fan_in"][0] == "Y"
    ]
    assert sig_non_atd == ["Non-ATD #14", "Non-ATD #15"]


def test_table_vii_modification_frequencies():
    """Validates Table VII: 2.31x fewer modifications in ATD files vs Non-ATD files."""
    comparator = PaperMetricsComparator()
    comps = comparator.compare_table_vii_modifications()

    for c in comps:
        assert c["match"] is True

    atd_avg = TABLE_VII_CHANGE_DISTRIBUTIONS["atd"]["avg_change"]
    non_atd_avg = TABLE_VII_CHANGE_DISTRIBUTIONS["non_atd"]["avg_change"]

    assert atd_avg == 6.981
    assert non_atd_avg == 16.115
    assert round(non_atd_avg / atd_avg, 2) == 2.31


def test_table_viii_partial_spearman_correlations():
    """Validates Table VIII: Negative correlation with cyclomatic complexity in ATD files."""
    comparator = PaperMetricsComparator()
    comps = comparator.compare_table_viii_correlations()

    for c in comps:
        assert c["match"] is True

    atd = TABLE_VIII_PARTIAL_CORRELATIONS["atd"]
    non_atd = TABLE_VIII_PARTIAL_CORRELATIONS["non_atd"]

    # ATD: positive with FAN-IN/OUT, negative with complexity (avoidance!)
    assert atd["fan_in"]["r"] == 0.241
    assert atd["fan_out"]["r"] == 0.175
    assert atd["complexity"]["r"] == -0.089

    # Non-ATD: positive across all three metrics
    assert non_atd["fan_in"]["r"] == 0.298
    assert non_atd["fan_out"]["r"] == 0.533
    assert non_atd["complexity"]["r"] == 0.313
