"""Unit tests for Checkpoint 5: Statistical Analytics & Debt Paradox Risk Engine."""

import pytest
from archdebt_lens.models.schemas import FileMetricRecord, LifecycleStage
from archdebt_lens.stats.non_parametric import (
    calculate_cliffs_delta,
    calculate_mann_whitney_u,
    check_normality_anderson,
)
from archdebt_lens.stats.correlation import partial_spearman_correlation
from archdebt_lens.stats.paradox_risk import DebtParadoxEvaluator


def test_cliffs_delta_and_mann_whitney():
    # Intro: lower connectivity
    intro = [1.0, 2.0, 1.0, 3.0, 2.0, 1.0, 4.0, 2.0]
    # Payment: higher connectivity
    payment = [5.0, 8.0, 12.0, 6.0, 9.0, 14.0, 10.0, 7.0]

    stat, p_val, is_sig = calculate_mann_whitney_u(intro, payment)
    assert is_sig is True
    assert p_val < 0.01

    delta, magnitude = calculate_cliffs_delta(payment, intro)
    assert delta > 0.474
    assert magnitude == "large"


def test_partial_spearman_correlation():
    # Synthetic dataset where complexity and changes are negatively correlated
    # while controlling for SLOC variations
    complexity = [12.0, 45.0, 18.0, 80.0, 25.0, 95.0, 30.0, 110.0, 40.0, 150.0]
    changes =    [18.0,  5.0, 15.0,  2.0, 12.0,  1.0, 11.0,   1.0,  9.0,   0.0]
    sloc =       [100.0, 250.0, 120.0, 400.0, 200.0, 500.0, 220.0, 600.0, 300.0, 700.0]

    r, p_val, ci = partial_spearman_correlation(complexity, changes, sloc)
    assert r < -0.4
    assert p_val < 0.05


def test_debt_paradox_evaluator_camel_endpoint():
    # In Table III of the paper:
    # Endpoint.java FAN-IN at intro = 11, FAN-IN at payment = 196
    intro_rec = FileMetricRecord(
        file_path="org/apache/camel/Endpoint.java",
        commit_hash="intro1",
        stage=LifecycleStage.INTRODUCTION,
        fan_in=11,
        fan_out=0,
        sloc=100,
        cyclomatic_complexity=5.0,
    )

    pay_rec = FileMetricRecord(
        file_path="org/apache/camel/Endpoint.java",
        commit_hash="77b260b6",
        stage=LifecycleStage.PAYMENT,
        fan_in=196,
        fan_out=5,
        sloc=180,
        cyclomatic_complexity=12.0,
    )

    risk = DebtParadoxEvaluator.evaluate_class_risk(
        "org/apache/camel/Endpoint.java", intro_rec, pay_rec
    )

    assert risk.is_paradox_risk is True
    assert risk.risk_level == "CRITICAL"
    assert risk.fan_in_growth_percent > 1000.0
    assert "single point of failure" in risk.recommendation.lower()
