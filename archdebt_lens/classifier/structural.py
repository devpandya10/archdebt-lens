"""
Structural dependency graph verifier for architectural technical debt.
Validates whether a commit actually impacts architectural modularity.
"""

from typing import Dict, List, Set, Tuple
from archdebt_lens.graph.dependency import DependencyGraphBuilder


class StructuralATDVerifier:
    """Verifies structural architectural debt by inspecting graph topology and diffs."""

    @staticmethod
    def verify_modularity_impact(
        builder_before: DependencyGraphBuilder,
        builder_after: DependencyGraphBuilder,
        affected_files: List[str],
    ) -> Tuple[float, List[str]]:
        """
        Evaluates structural impact score [0.0, 1.0] and returns structural indicators.
        """
        reasons: List[str] = []
        score = 0.0

        # 1. Check for removed files (common in modularity refactoring, e.g. -44.5% in paper)
        before_nodes = set(builder_before.graph.nodes)
        after_nodes = set(builder_after.graph.nodes)
        removed_nodes = before_nodes - after_nodes

        if removed_nodes:
            score += 0.3
            reasons.append(f"Removed {len(removed_nodes)} files during modularity restructuring")

        # 2. Check for cycle resolution or introduction
        cycles_before = len(builder_before.detect_cycles())
        cycles_after = len(builder_after.detect_cycles())

        if cycles_before > 0 and cycles_after == 0:
            score += 0.4
            reasons.append(f"Eliminated {cycles_before} circular dependency cycle(s)")
        elif cycles_after > cycles_before:
            score += 0.35
            reasons.append(f"Introduced {cycles_after - cycles_before} new circular dependency cycle(s)")

        # 3. Check for high dependency shift (FAN-IN / FAN-OUT)
        total_fan_in_shift = 0
        common_files = before_nodes.intersection(after_nodes).intersection(set(affected_files))
        for f in common_files:
            fi_before = builder_before.get_fan_in(f)
            fi_after = builder_after.get_fan_in(f)
            diff = abs(fi_after - fi_before)
            total_fan_in_shift += diff

        if total_fan_in_shift >= 3:
            score += 0.3
            reasons.append(f"Significant dependency shift (total ΔFAN-IN = {total_fan_in_shift})")

        return round(min(1.0, score), 3), reasons
