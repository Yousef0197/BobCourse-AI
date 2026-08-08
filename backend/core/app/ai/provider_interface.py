"""
AI Provider Interface — abstract base class for all AI providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AIAnalysisResult:
    """Structured output from any AI provider."""
    summary: str
    sentiment: str  # "positive" | "neutral" | "negative" | "mixed"
    themes: list[str]
    improvement_areas: list[str]
    provider_used: str


class AIProviderInterface(ABC):
    """Abstract interface all AI providers must implement."""

    @abstractmethod
    def analyze(self, comments: list[str]) -> AIAnalysisResult:
        """
        Analyze a list of anonymized text comments.

        Args:
            comments: Pre-masked comments (PII already removed).

        Returns:
            AIAnalysisResult with structured insights.
        """
