"""
Metrics calculation for dependency connectivity, complexity, and centralization.
"""

from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from archdebt_lens.graph.dependency import DependencyGraphBuilder
from archdebt_lens.models.schemas import FileMetricRecord, LifecycleStage


class MetricsCalculator:
    """Computes code connectivity and complexity metrics from dependency graphs."""

    @staticmethod
    def calculate_file_metrics(
        builder: DependencyGraphBuilder,
        file_path: str,
        commit_hash: str = "HEAD",
        stage: LifecycleStage = LifecycleStage.PAYMENT,
        modification_count: int = 0,
    ) -> FileMetricRecord:
        """Computes comprehensive metrics for an individual file."""
        norm_path = str(Path(file_path))
        entity = builder.entities.get(norm_path)
        sloc = entity.sloc if entity else 1
        complexity = float(entity.cyclomatic_complexity) if entity else 1.0

        fan_in = builder.get_fan_in(norm_path)
        fan_out = builder.get_fan_out(norm_path)

        return FileMetricRecord(
            file_path=norm_path,
            commit_hash=commit_hash,
            stage=stage,
            fan_in=fan_in,
            fan_out=fan_out,
            sloc=sloc,
            cyclomatic_complexity=complexity,
            modification_count=modification_count,
        )

    @staticmethod
    def calculate_all_metrics(
        builder: DependencyGraphBuilder,
        commit_hash: str = "HEAD",
        stage: LifecycleStage = LifecycleStage.PAYMENT,
        modification_counts: Optional[Dict[str, int]] = None,
    ) -> Dict[str, FileMetricRecord]:
        """Calculates metrics for all files in the dependency graph."""
        mod_counts = modification_counts or {}
        results = {}
        for file_path in builder.entities.keys():
            mod_count = mod_counts.get(file_path, 0)
            record = MetricsCalculator.calculate_file_metrics(
                builder, file_path, commit_hash, stage, mod_count
            )
            results[file_path] = record
        return results

    @staticmethod
    def calculate_summary_stats(metrics: Dict[str, FileMetricRecord]) -> Dict[str, float]:
        """Calculates summary statistics (average, max, etc.) matching Table IV in the paper."""
        if not metrics:
            return {
                "file_count": 0,
                "fan_in_avg": 0.0,
                "fan_in_max": 0.0,
                "fan_out_avg": 0.0,
                "fan_out_max": 0.0,
            }

        fan_ins = [m.fan_in for m in metrics.values()]
        fan_outs = [m.fan_out for m in metrics.values()]

        return {
            "file_count": float(len(metrics)),
            "fan_in_avg": float(np.mean(fan_ins)),
            "fan_in_max": float(np.max(fan_ins)),
            "fan_out_avg": float(np.mean(fan_outs)),
            "fan_out_max": float(np.max(fan_outs)),
        }
