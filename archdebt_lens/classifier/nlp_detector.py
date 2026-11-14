"""
NLP-based Self-Admitted Technical Debt (SATD) detector for architectural issues.
Extracts semantic cues from commit messages, issue summaries, and pull requests.
"""

import re
from typing import Dict, List, Tuple


class NLPATDDetector:
    """Analyzes text for architectural technical debt (ATD) indicators."""

    # Keywords specifically indicating Architectural Debt (Violation of Modularity)
    ARCH_KEYWORDS = [
        r"\bmodular(?:ity)?\b",
        r"\barchitectur(?:e|al)\b",
        r"\bcoupl(?:ing|ed)\b",
        r"\bdecoupl(?:e|ing|ed)\b",
        r"\bdependenc(?:y|ies)\b",
        r"\bcircular\b",
        r"\bcentraliz(?:e|ation|ed)\b",
        r"\bboundar(?:y|ies)\b",
        r"\bhierarch(?:y|ical)\b",
        r"\brestructur(?:e|ing|ed)\b",
        r"\bspaghetti\b",
        r"\blayer(?:s|ing)?\b",
        r"\bencapsulat(?:e|ion)\b",
    ]

    # General Self-Admitted Technical Debt (SATD) indicators
    SATD_KEYWORDS = [
        r"\bworkaround\b",
        r"\bhack\b",
        r"\btodo\b",
        r"\bfixme\b",
        r"\btemporary\b",
        r"\brefactor\b",
        r"\bcleanup\b",
        r"\bdebt\b",
        r"\btrade-?off\b",
        r"\brotten\b",
        r"\bsmell\b",
    ]

    def __init__(self):
        self.arch_patterns = [re.compile(p, re.IGNORECASE) for p in self.ARCH_KEYWORDS]
        self.satd_patterns = [re.compile(p, re.IGNORECASE) for p in self.SATD_KEYWORDS]

    def score_text(self, text: str) -> Tuple[float, List[str]]:
        """
        Calculates an ATD confidence score [0.0, 1.0] based on textual cues.
        Returns (score, list_of_matched_indicators).
        """
        if not text:
            return 0.0, []

        matches: List[str] = []

        arch_matches = 0
        for pattern in self.arch_patterns:
            found = pattern.findall(text)
            if found:
                arch_matches += len(found)
                matches.append(found[0].lower())

        satd_matches = 0
        for pattern in self.satd_patterns:
            found = pattern.findall(text)
            if found:
                satd_matches += len(found)
                matches.append(found[0].lower())

        # If it has both architectural words and SATD debt words, confidence is high
        if arch_matches >= 1 and satd_matches >= 1:
            raw_score = 0.5 + min(0.5, (arch_matches * 0.15 + satd_matches * 0.1))
        elif arch_matches >= 1:
            raw_score = min(0.6, arch_matches * 0.25)
        elif satd_matches >= 1:
            # General code debt, but might not be architectural debt
            raw_score = min(0.35, satd_matches * 0.15)
        else:
            raw_score = 0.0

        return round(min(1.0, raw_score), 3), list(set(matches))
