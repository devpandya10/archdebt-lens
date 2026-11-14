"""Unit tests for Checkpoint 1: Domain models, validation & persistence."""

from datetime import datetime, timezone
import pytest
from archdebt_lens.models.schemas import (
    ATDItem,
    CommitSnapshot,
    FileMetricRecord,
    LifecycleTrace,
    LifecycleStage,
    DebtType,
    ArtifactSource,
)
from archdebt_lens.models.storage import DataStore


def test_atd_item_creation():
    item = ATDItem(
        id="CAMEL-789",
        project="apache-camel",
        debt_type=DebtType.VIOMOD,
        source=ArtifactSource.IS,
        summary="Modularity violation in Builder hierarchy",
        payment_commit="77b260b6"
    )
    assert item.id == "CAMEL-789"
    assert item.debt_type == DebtType.VIOMOD
    assert item.is_validated is True


def test_file_metric_computed_fields():
    metric = FileMetricRecord(
        file_path="org/apache/camel/Endpoint.java",
        commit_hash="77b260b6",
        stage=LifecycleStage.PAYMENT,
        fan_in=196,
        fan_out=5,
        sloc=200,
        cyclomatic_complexity=12.5,
        modification_count=4
    )
    assert metric.fan_in == 196
    assert metric.fan_in_per_sloc == round(196 / 200, 6)
    assert metric.fan_out_per_sloc == round(5 / 200, 6)


def test_datastore_persistence(tmp_path):
    db_file = str(tmp_path / "test.db")
    store = DataStore(db_path=db_file)

    item = ATDItem(
        id="ATD-1",
        project="apache-camel",
        summary="Endpoint restructuring",
        payment_commit="77b260b6"
    )
    store.add_item(item)
    fetched = store.get_item("ATD-1")
    assert fetched is not None
    assert fetched.summary == "Endpoint restructuring"

    trace = LifecycleTrace(
        atd_id="ATD-1",
        intro_commit="c0ffee1",
        payment_commit="77b260b6",
        payment_interval_days=45.5,
        files_at_intro=["Endpoint.java", "ChoiceBuilder.java"],
        files_at_payment=["Endpoint.java"],
        files_removed=["ChoiceBuilder.java"]
    )
    store.save_trace(trace)
    fetched_trace = store.get_trace("ATD-1")
    assert fetched_trace is not None
    assert len(fetched_trace.files_removed) == 1
    assert "ChoiceBuilder.java" in fetched_trace.files_removed
