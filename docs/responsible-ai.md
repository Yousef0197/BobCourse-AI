# Responsible AI

## Principles

BobCourse-AI's AI module is designed around five principles:

1. **Transparency** — All AI-generated outputs are clearly labelled as such
2. **Human Oversight** — Every insight requires human review before action
3. **Privacy** — PII is masked before any AI processing
4. **Non-maleficence** — Results must not be used to penalise individual instructors
5. **Fallback Availability** — The system works fully without any external AI API

## PII Protection

Before any text comment is processed by AI:

1. All comments are passed through the PII masking utility (`app/ai/pii_masking.py`)
2. The following patterns are replaced:
   - Email addresses → `[EMAIL]`
   - Phone numbers → `[PHONE]`
   - Student ID patterns (S1234567, STU-123456) → `[STUDENT_ID]`
   - Name patterns ("My name is John Smith") → `[NAME]`
3. Comments are flagged in the database (`text_comments.is_flagged = true`) when PII was detected
4. Original (unmasked) comments are never sent to any external API

## AI Provider Architecture

```python
AIProviderInterface (abstract)
├── OfflineFallbackProvider  ← always available, no API key
└── OpenAIProvider           ← requires OPENAI_API_KEY env var
```

Provider selection at runtime:
```python
if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
    return OpenAIProvider()
return OfflineFallbackProvider()  # default
```

### OfflineFallbackProvider

Keyword-heuristic analysis that:
- Works with zero external dependencies
- Classifies sentiment as positive/negative/mixed/neutral based on keyword counts
- Identifies recurring themes (teaching, materials, workload, pacing, etc.)
- Suggests improvement areas
- Labels all results as `provider_used: "offline_fallback"`

### OpenAIProvider

Optional GPT-based analysis:
- Only activates when `OPENAI_API_KEY` is set
- Degrades gracefully to `OfflineFallbackProvider` on any error
- Sends only masked comments to OpenAI

## AI Analysis Output Structure

```json
{
  "summary": "Analysis of N comments. Overall sentiment: positive.",
  "sentiment": "positive | neutral | negative | mixed",
  "themes": ["Teaching", "Course Materials"],
  "improvement_areas": ["More Examples", "Clearer Explanations"],
  "provider_used": "offline_fallback | openai",
  "human_reviewed": false,
  "disclaimer_acknowledged": false
}
```

## Mandatory Disclaimer

Every AI insight is served with this disclaimer:

> "AI-generated content may be incomplete or inaccurate regardless of the analysis provider used. Human review is required before acting on these insights. Student identities cannot be inferred from this output."

The frontend requires a per-view acknowledgement checkbox before displaying AI insight content. This UI acknowledgement is not persisted; the stored `disclaimer_acknowledged` flag is recorded when an administrator completes the human-review workflow.

## Human Review Workflow

1. Admin triggers AI analysis (`POST /api/v1/ai-insights/campaigns/{id}/trigger`)
2. System masks PII → runs provider → stores insight
3. Admin or instructor views insight (must acknowledge disclaimer)
4. Admin marks as reviewed (`POST /api/v1/ai-insights/insights/{id}/review`)
5. `human_reviewed: true` and `reviewed_at` timestamp are recorded

## Limitations

- The offline fallback is heuristic, not semantic — it cannot understand context
- Keyword matching may produce false positives for sentiment
- AI results should never be the sole basis for instructor performance evaluation
- OpenAI analysis quality depends on comment volume and quality
- No model versioning or audit trail of AI model changes (out of scope for MVP)

## Testing

Unit tests in `tests/test_responsible_ai.py` verify:
- PII masking for all pattern types
- Offline fallback sentiment classification
- Empty comment handling
- Required output fields


