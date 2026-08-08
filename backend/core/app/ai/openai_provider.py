"""
OpenAI provider stub — guarded by OPENAI_API_KEY environment variable.
Returns a structured AIAnalysisResult from GPT if the key is present.
"""
from app.ai.provider_interface import AIProviderInterface, AIAnalysisResult
from app.core.config import settings


class OpenAIProvider(AIProviderInterface):
    """
    OpenAI GPT-based comment analysis.
    Only active when OPENAI_API_KEY is set in environment.
    Falls back to offline provider if key is missing.
    """

    def analyze(self, comments: list[str]) -> AIAnalysisResult:
        if not settings.OPENAI_API_KEY:
            # Guard: never call OpenAI without a key
            from app.ai.offline_fallback import OfflineFallbackProvider
            return OfflineFallbackProvider().analyze(comments)

        try:
            import openai  # optional dependency
        except ImportError:
            from app.ai.offline_fallback import OfflineFallbackProvider
            return OfflineFallbackProvider().analyze(comments)

        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            combined = "\n".join(f"- {c}" for c in comments)
            prompt = (
                "You are an academic quality assurance assistant. "
                "Analyze the following anonymized student course evaluation comments. "
                "Respond with JSON containing: summary (string), sentiment (positive|neutral|negative|mixed), "
                "themes (list of strings), improvement_areas (list of strings).\n\n"
                f"Comments:\n{combined}"
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=500,
            )
            import json
            raw = json.loads(response.choices[0].message.content)
            return AIAnalysisResult(
                summary=raw.get("summary", ""),
                sentiment=raw.get("sentiment", "neutral"),
                themes=raw.get("themes", []),
                improvement_areas=raw.get("improvement_areas", []),
                provider_used="openai",
            )
        except Exception:
            # On any failure, degrade gracefully to offline fallback
            from app.ai.offline_fallback import OfflineFallbackProvider
            return OfflineFallbackProvider().analyze(comments)
