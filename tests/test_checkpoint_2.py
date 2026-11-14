"""Unit tests for Checkpoint 2: Git Mining & Lifecycle Tracing."""

import os
from pathlib import Path
import git
import pytest
from archdebt_lens.miner.git_miner import GitRepoMiner
from archdebt_lens.miner.lifecycle import LifecycleTracer
from archdebt_lens.models.schemas import ATDItem, DebtType, ArtifactSource


@pytest.fixture
def mock_git_repo(tmp_path):
    """Creates a mock git repository with introduction, intermediate, and payment commits."""
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    repo = git.Repo.init(repo_dir)

    # Commit 1: Introduction of Endpoint.java and ChoiceBuilder.java
    f1 = repo_dir / "Endpoint.java"
    f1.write_text("public class Endpoint {}")
    f2 = repo_dir / "ChoiceBuilder.java"
    f2.write_text("public class ChoiceBuilder {}")
    repo.index.add(["Endpoint.java", "ChoiceBuilder.java"])
    c1 = repo.index.commit("Initial introduction of Endpoint and Builder")

    # Commit 2: Intermediate change to Endpoint.java
    f1.write_text("public class Endpoint { /* intermediate */ }")
    repo.index.add(["Endpoint.java"])
    c2 = repo.index.commit("Intermediate fix to Endpoint")

    # Commit 3: Payment - Removal of ChoiceBuilder.java, refactoring of Endpoint.java
    f1.write_text("public class Endpoint { /* repaid modularity debt */ }")
    os.remove(f2)
    repo.index.add(["Endpoint.java"])
    repo.index.remove(["ChoiceBuilder.java"])
    c3 = repo.index.commit("CAMEL-789: Fix modularity debt by removing ChoiceBuilder")

    return {
        "repo_path": str(repo_dir),
        "intro_hash": c1.hexsha,
        "intermediate_hash": c2.hexsha,
        "payment_hash": c3.hexsha,
    }


def test_git_miner_commit_snapshot(mock_git_repo):
    miner = GitRepoMiner(mock_git_repo["repo_path"])
    snapshot = miner.get_commit_snapshot(mock_git_repo["payment_hash"])

    assert snapshot.commit_hash == mock_git_repo["payment_hash"]
    assert "CAMEL-789" in snapshot.message
    assert "Endpoint.java" in snapshot.affected_files or "ChoiceBuilder.java" in snapshot.affected_files


def test_git_miner_diff_and_modifications(mock_git_repo):
    miner = GitRepoMiner(mock_git_repo["repo_path"])

    added, modified, deleted = miner.get_commit_file_diff(
        mock_git_repo["intro_hash"], mock_git_repo["payment_hash"]
    )
    assert "ChoiceBuilder.java" in deleted
    assert "Endpoint.java" in modified

    mods = miner.count_file_modifications(
        "Endpoint.java", mock_git_repo["intro_hash"], mock_git_repo["payment_hash"]
    )
    assert mods == 2


def test_lifecycle_tracer(mock_git_repo):
    miner = GitRepoMiner(mock_git_repo["repo_path"])
    tracer = LifecycleTracer(miner)

    item = ATDItem(
        id="CAMEL-789",
        project="camel",
        debt_type=DebtType.VIOMOD,
        source=ArtifactSource.IS,
        summary="Modularity violation in Builder",
        payment_commit=mock_git_repo["payment_hash"],
        intro_commit=mock_git_repo["intro_hash"],
    )

    trace = tracer.trace_lifecycle(item)
    assert trace.intro_commit == mock_git_repo["intro_hash"]
    assert trace.payment_commit == mock_git_repo["payment_hash"]
    assert "ChoiceBuilder.java" in trace.files_removed
    assert trace.intermediate_commit_count >= 1
