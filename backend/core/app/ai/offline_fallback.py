"""
Offline fallback AI provider — keyword heuristics, no API key required.
Always available; used when no external AI is configured.
"""
from app.ai.provider_interface import AIProviderInterface, AIAnalysisResult

_POSITIVE_KEYWORDS = {
    "excellent", "great", "amazing", "outstanding", "wonderful", "fantastic",
    "helpful", "clear", "organized", "engaging", "knowledgeable", "thorough",
    "enjoyed", "learned", "loved", "best", "good", "well", "effective",
}

_NEGATIVE_KEYWORDS = {
    "poor", "bad", "terrible", "awful", "boring", "confusing", "unclear",
    "disorganized", "unhelpful", "difficult", "hard", "worst", "disappointing",
    "frustrating", "lost", "slow", "late", "unresponsive", "unfair",
}

_THEME_KEYWORDS = {
    "teaching": ["teach", "explain", "lecture", "instructor", "professor"],
    "course_materials": ["slides", "material", "textbook", "notes", "resource"],
    "workload": ["workload", "assignment", "homework", "exam", "test", "quiz"],
    "pacing": ["pace", "fast", "slow", "rushed", "time"],
    "feedback": ["feedback", "grade", "response", "comment"],
    "accessibility": ["accessible", "support", "office hours", "available"],
}

_IMPROVEMENT_PHRASES = {
    "better materials": ["improve", "better", "update", "material", "slides"],
    "clearer explanations": ["clearer", "explain", "confusing", "understand"],
    "more examples": ["example", "practice", "exercise", "hands-on"],
    "more feedback": ["feedback", "grade", "response"],
    "better pacing": ["slow down", "too fast", "pace", "rushed"],
}


class OfflineFallbackProvider(AIProviderInterface):
    """
    Keyword-heuristic AI provider.
    Works with zero external dependencies — no API key required.
    Results are labelled "offline_fallback" so reviewers know AI was not used.
    """

    def analyze(self, comments: list[str]) -> AIAnalysisResult:
        if not comments:
            return AIAnalysisResult(
                summary="No comments were submitted for this campaign.",
                sentiment="neutral",
                themes=[],
                improvement_areas=[],
                provider_used="offline_fallback",
            )

        combined = " ".join(c.lower() for c in comments)
        words = set(combined.split())

        # ── Sentiment ───────────────────────────────────────────────────────
        pos_count = sum(1 for w in _POSITIVE_KEYWORDS if w in combined)
        neg_count = sum(1 for w in _NEGATIVE_KEYWORDS if w in combined)

        if pos_count > neg_count * 2:
            sentiment = "positive"
        elif neg_count > pos_count * 2:
            sentiment = "negative"
        elif pos_count > 0 and neg_count > 0:
            sentiment = "mixed"
        else:
            sentiment = "neutral"

        # ── Themes ─────────────────────────────────────────────────────────
        themes = []
        for theme, kws in _THEME_KEYWORDS.items():
            if any(kw in combined for kw in kws):
                themes.append(theme.replace("_", " ").title())

        # ── Improvement areas ───────────────────────────────────────────────
        improvement_areas = []
        for area, kws in _IMPROVEMENT_PHRASES.items():
            if any(kw in combined for kw in kws):
                improvement_areas.append(area.replace("_", " ").title())

        # ── Summary ─────────────────────────────────────────────────────────
        n = len(comments)
        summary = (
            f"Analysis of {n} comment{'s' if n != 1 else ''} "
            f"using keyword heuristics. "
            f"Overall sentiment: {sentiment}."
        )
        if themes:
            summary += f" Key themes: {', '.join(themes[:3])}."
        if improvement_areas:
            summary += f" Suggested improvements: {', '.join(improvement_areas[:2])}."

        return AIAnalysisResult(
            summary=summary,
            sentiment=sentiment,
            themes=themes,
            improvement_areas=improvement_areas,
            provider_used="offline_fallback",
        )
