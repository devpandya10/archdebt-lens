"""
Lifecycle State Machine and Coordinator for ATD items.
Connects introduction to payment and traces structural evolution.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from archdebt_lens.miner.git_miner import GitRepoMiner
from archdebt_lens.models.schemas import ATDItem, LifecycleTrace, LifecycleStage


class LifecycleTracer:
    """Orchestrates the lifecycle extraction for an ATD item across Git history."""

    def __init__(self, miner: GitRepoMiner):
        self.miner = miner

    def trace_lifecycle(
        self,
        item: ATDItem,
        intro_commit: Optional[str] = None,
        payment_commit: Optional[str] = None,
    ) -> LifecycleTrace:
        """
        Builds a comprehensive LifecycleTrace between introduction and payment commits.
        """
        pay_hash = payment_commit or item.payment_commit
        if not pay_hash:
            raise ValueError(f"No payment commit provided for item {item.id}")

        pay_snapshot = self.miner.get_commit_snapshot(pay_hash)

        # Determine introduction commit if not explicitly provided
        in_hash = intro_commit or item.intro_commit
        if not in_hash:
            # Trace introduction using the first affected file from payment
            if pay_snapshot.affected_files:
                sample_file = pay_snapshot.affected_files[0]
                in_hash = self.miner.trace_introduction_commit(sample_file, pay_hash)
            if not in_hash:
                in_hash = pay_snapshot.parent_hash or pay_hash

        intro_snapshot = self.miner.get_commit_snapshot(in_hash)

        # Calculate payment interval
        interval_seconds = abs((pay_snapshot.timestamp - intro_snapshot.timestamp).total_seconds())
        interval_days = round(interval_seconds / 86400.0, 2)

        # Determine file changes between intro and payment
        added, modified, deleted = self.miner.get_commit_file_diff(in_hash, pay_hash)

        files_at_intro = list(set(intro_snapshot.affected_files).union(modified, deleted))
        files_at_payment = list(set(pay_snapshot.affected_files).union(modified, added))
        files_removed = list(deleted)

        # Count intermediate commits
        try:
            rev_range = f"{in_hash}..{pay_hash}"
            intermediate_commits = list(self.miner.repo.iter_commits(rev_range))
            intermediate_count = len(intermediate_commits)
        except Exception:
            intermediate_count = 0

        return LifecycleTrace(
            atd_id=item.id,
            intro_commit=in_hash,
            payment_commit=pay_hash,
            payment_interval_days=interval_days,
            files_at_intro=files_at_intro,
            files_at_payment=files_at_payment,
            files_removed=files_removed,
            intermediate_commit_count=intermediate_count,
            metrics_intro={},
            metrics_payment={},
        )
