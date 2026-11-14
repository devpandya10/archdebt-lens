"""Unit tests for Checkpoint 8: Replication Benchmark & End-to-End System Testing."""

import pytest
from archdebt_lens.replication.benchmark import ReplicationBenchmark


def test_camel_worked_example_replication():
    results = ReplicationBenchmark.replicate_camel_worked_example()

    assert results["removed_files_count"] == 3
    # In Section IV of paper:
    # Directional test shows FAN-IN repayment > introduction (p < 0.05) and large effect size
    assert results["fan_in"]["is_significant"] is True
    assert results["fan_in"]["p_value"] < 0.05
    assert results["fan_in"]["cliffs_delta"] > 0.474
    assert results["fan_in"]["magnitude"] == "large"


def test_paper_core_hypotheses_validation():
    hypotheses = ReplicationBenchmark.verify_paper_hypotheses()

    assert hypotheses["H1_repayment_increases_fan_in"] is True
    assert hypotheses["H2_atd_files_modified_less"] is True
    assert hypotheses["H3_code_avoidance_negative_correlation"] is True
