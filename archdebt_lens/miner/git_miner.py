"""
Git repository miner for ATD lifecycle analysis.
Extracts commit history, file modification frequencies, diffs, and blamelines.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import git
from archdebt_lens.models.schemas import CommitSnapshot


class GitRepoMiner:
    """Mines a Git repository for commits, diffs, and file modification history."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")
        self.repo = git.Repo(self.repo_path)

    def get_commit_snapshot(self, commit_hash: str) -> CommitSnapshot:
        """Retrieves metadata and affected files for a specific commit."""
        commit = self.repo.commit(commit_hash)
        parent_hash = commit.parents[0].hexsha if commit.parents else None

        affected_files: List[str] = []
        if commit.parents:
            diffs = commit.parents[0].diff(commit)
            for d in diffs:
                if d.b_path:
                    affected_files.append(d.b_path)
                elif d.a_path:
                    affected_files.append(d.a_path)
        else:
            # Root commit
            affected_files = list(commit.stats.files.keys())

        return CommitSnapshot(
            commit_hash=commit.hexsha,
            parent_hash=parent_hash,
            author=str(commit.author),
            timestamp=datetime.fromtimestamp(commit.committed_date, tz=timezone.utc),
            message=commit.message.strip(),
            affected_files=affected_files,
        )

    def count_file_modifications(
        self, file_path: str, from_commit: str, to_commit: str
    ) -> int:
        """
        Counts the number of commits that modified a specific file
        between from_commit (introduction) and to_commit (payment).
        """
        try:
            rev_range = f"{from_commit}..{to_commit}"
            commits = list(self.repo.iter_commits(rev_range, paths=file_path))
            return len(commits)
        except Exception:
            return 0

    def get_commit_file_diff(
        self, from_commit: str, to_commit: str
    ) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        Compares file trees between two commits.
        Returns (added_files, modified_files, deleted_files).
        """
        c_from = self.repo.commit(from_commit)
        c_to = self.repo.commit(to_commit)
        diff_index = c_from.diff(c_to)

        added: Set[str] = set()
        modified: Set[str] = set()
        deleted: Set[str] = set()

        for d in diff_index:
            if d.new_file:
                if d.b_path:
                    added.add(d.b_path)
            elif d.deleted_file:
                if d.a_path:
                    deleted.add(d.a_path)
            else:
                if d.b_path:
                    modified.add(d.b_path)

        return added, modified, deleted

    def trace_introduction_commit(
        self, file_path: str, payment_commit: str, search_keywords: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Traces the historical commit where the file or debt pattern was first introduced.
        Uses reverse commit traversal and log matching.
        """
        try:
            commits = list(self.repo.iter_commits(payment_commit, paths=file_path))
            if not commits:
                return None

            if search_keywords:
                for commit in reversed(commits):
                    msg = commit.message.lower()
                    if any(kw.lower() in msg for kw in search_keywords):
                        return commit.hexsha

            # Default: the initial commit that introduced the file
            return commits[-1].hexsha
        except Exception:
            return None
