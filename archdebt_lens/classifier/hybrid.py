"""
Hybrid classifier combining NLP and Structural Dependency analysis
to accurately classify Architectural Technical Debt (ATD).
"""

from typing import Dict, List, Optional, Tuple
from archdebt_lens.classifier.nlp_detector import NLPATDDetector
from archdebt_lens.classifier.structural import StructuralATDVerifier
from archdebt_lens.graph.dependency import DependencyGraphBuilder


class ClassificationResult:
    def __init__(
        self,
        predicted_category: str,
        confidence: float,
        nlp_score: float,
        structural_score: float,
        explanation: List[str],
    ):
        self.predicted_category = predicted_category
        self.confidence = confidence
        self.nlp_score = nlp_score
        self.structural_score = structural_score
        self.explanation = explanation

    def to_dict(self) -> Dict:
        return {
            "predicted_category": self.predicted_category,
            "confidence": self.confidence,
            "nlp_score": self.nlp_score,
            "structural_score": self.structural_score,
            "explanation": self.explanation,
        }


class HybridATDClassifier:
    """Classifies commits/issues into True ATD, Code Debt, or Benign Change."""

    def __init__(self, weight_nlp: float = 0.45, weight_structural: float = 0.55):
        self.nlp_detector = NLPATDDetector()
        self.structural_verifier = StructuralATDVerifier()
        self.weight_nlp = weight_nlp
        self.weight_structural = weight_structural

    def classify(
        self,
        text_content: str,
        builder_before: Optional[DependencyGraphBuilder] = None,
        builder_after: Optional[DependencyGraphBuilder] = None,
        affected_files: Optional[List[str]] = None,
    ) -> ClassificationResult:
        """Runs the hybrid classification pipeline."""
        nlp_score, nlp_cues = self.nlp_detector.score_text(text_content)

        structural_score = 0.0
        structural_cues: List[str] = []
        if builder_before and builder_after and affected_files:
            structural_score, structural_cues = self.structural_verifier.verify_modularity_impact(
                builder_before, builder_after, affected_files
            )

        # Calculate blended confidence
        if builder_before and builder_after:
            blended = (self.weight_nlp * nlp_score) + (self.weight_structural * structural_score)
        else:
            blended = nlp_score

        explanations = []
        if nlp_cues:
            explanations.append(f"Textual indicators: {', '.join(nlp_cues)}")
        if structural_cues:
            explanations.extend(structural_cues)

        # Categorize
        if blended >= 0.50 and (structural_score >= 0.3 or nlp_score >= 0.7):
            category = "TRUE_ATD"
        elif nlp_score >= 0.3 or structural_score >= 0.3:
            category = "CODE_DEBT"
        else:
            category = "BENIGN_CHANGE"

        return ClassificationResult(
            predicted_category=category,
            confidence=round(blended, 3),
            nlp_score=nlp_score,
            structural_score=structural_score,
            explanation=explanations,
        )
