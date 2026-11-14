"""Unit tests for Checkpoint 4: Hybrid ATD Detection Pipeline."""

import pytest
from archdebt_lens.classifier.nlp_detector import NLPATDDetector
from archdebt_lens.classifier.structural import StructuralATDVerifier
from archdebt_lens.classifier.hybrid import HybridATDClassifier
from archdebt_lens.graph.dependency import DependencyGraphBuilder


def test_nlp_detector():
    detector = NLPATDDetector()

    # Modularity ATD message
    atd_text = "Refactor modularity: decouple SendProcessor and remove circular dependency workaround"
    score, cues = detector.score_text(atd_text)
    assert score >= 0.6
    assert "modularity" in cues or "circular" in cues

    # Simple code debt
    code_debt_text = "TODO: fix typo in variable name"
    score2, cues2 = detector.score_text(code_debt_text)
    assert score2 <= 0.35
    assert "todo" in cues2

    # Benign commit
    benign_text = "Update documentation README"
    score3, cues3 = detector.score_text(benign_text)
    assert score3 == 0.0


def test_hybrid_classifier_with_graph_diff():
    classifier = HybridATDClassifier()

    # Graph before: has 2 files with circular dependency
    g_before = DependencyGraphBuilder()
    g_before.add_file("A.java", "import B; public class A { private B b; }")
    g_before.add_file("B.java", "import A; public class B { private A a; }")
    g_before.build_edges()
    assert len(g_before.detect_cycles()) == 1

    # Graph after: B is refactored, circular dependency broken
    g_after = DependencyGraphBuilder()
    g_after.add_file("A.java", "import B; public class A { private B b; }")
    g_after.add_file("B.java", "public class B { /* decoupled */ }")
    g_after.build_edges()
    assert len(g_after.detect_cycles()) == 0

    text = "Break circular dependency between A and B to fix modularity architecture debt"
    result = classifier.classify(
        text_content=text,
        builder_before=g_before,
        builder_after=g_after,
        affected_files=["A.java", "B.java"]
    )

    assert result.predicted_category == "TRUE_ATD"
    assert result.confidence >= 0.55
    assert any("circular" in exp.lower() for exp in result.explanation)
