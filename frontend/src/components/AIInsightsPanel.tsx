/**
 * AI Insights Panel — shared privacy-aware component for admin/instructor.
 */
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import apiClient from '../lib/apiClient'
import { getCurrentUser } from '../lib/auth'

interface AIInsight {
  id: string
  campaign_id: string
  summary: string | null
  sentiment: string | null
  themes: string[] | null
  improvement_areas: string[] | null
  provider_used: string | null
  generated_at: string | null
  human_reviewed: boolean
  disclaimer_acknowledged: boolean
}

const DISCLAIMER =
  'AI-generated insights may be incomplete or inaccurate, regardless of the analysis provider used. ' +
  'These results require human review before any action is taken. ' +
  'Student anonymity is maintained; individual students must not be inferred from this output.'

export default function AIInsightsPanel({
  campaignId,
}: {
  campaignId: string
}) {
  const [showPanel, setShowPanel] = useState(false)
  const [disclaimerRead, setDisclaimerRead] = useState(false)
  const [triggering, setTriggering] = useState(false)
  const user = getCurrentUser()

  const {
    data: insight,
    isLoading,
    error,
    refetch,
  } = useQuery<AIInsight>({
    queryKey: ['ai-insight', campaignId],
    queryFn: async () => {
      const resp = await apiClient.get<AIInsight>(
        `/ai-insights/campaigns/${campaignId}`,
      )
      return resp.data
    },
    enabled: showPanel,
    retry: false,
  })

  async function handleTrigger() {
    setTriggering(true)

    try {
      await apiClient.post(
        `/ai-insights/campaigns/${campaignId}/trigger`,
      )
      await refetch()
    } finally {
      setTriggering(false)
    }
  }

  if (!showPanel) {
    return (
      <div className="ai-insights-launcher">
        <div>
          <span className="ai-insights-eyebrow">
            RESPONSIBLE AI
          </span>
          <strong>AI-assisted course insights</strong>
          <p>
            Review summarized themes and improvement opportunities from
            evaluation feedback.
          </p>
        </div>

        <button
          type="button"
          className="ai-insights-view-btn"
          onClick={() => setShowPanel(true)}
        >
          View AI Insights
        </button>
      </div>
    )
  }

  return (
    <section className="ai-insights-panel">
      <div className="ai-insights-header">
        <div>
          <span className="ai-insights-eyebrow">
            RESPONSIBLE AI
          </span>
          <h4>AI Insights</h4>
        </div>

        <span className="ai-insights-header__badge">
          Human oversight required
        </span>
      </div>

      <div className="ai-insights-disclaimer">
        <div className="ai-insights-disclaimer__icon">
          !
        </div>

        <div>
          <strong>Important disclaimer</strong>
          <p>{DISCLAIMER}</p>
        </div>
      </div>

      {!disclaimerRead ? (
        <label className="ai-insights-consent">
          <input
            type="checkbox"
            checked={disclaimerRead}
            onChange={(event) =>
              setDisclaimerRead(event.target.checked)
            }
          />

          <span>
            I understand this content is AI-generated and requires
            human review.
          </span>
        </label>
      ) : (
        <div className="ai-insights-acknowledged">
          <span>✓</span>
          Disclaimer acknowledged for this view
        </div>
      )}

      {disclaimerRead && (
        <div className="ai-insights-body">
          {isLoading && (
            <div className="ai-insights-state">
              Loading insights…
            </div>
          )}

          {error && (
            <div className="ai-insights-state">
              {user?.role === 'admin' ? (
                <>
                  <strong>No AI insights generated yet</strong>
                  <p>
                    Generate an analysis for this campaign when you are
                    ready to review the results.
                  </p>

                  <button
                    type="button"
                    className="ai-insights-generate-btn"
                    disabled={triggering}
                    onClick={handleTrigger}
                  >
                    {triggering
                      ? 'Generating…'
                      : 'Generate AI Insights'}
                  </button>
                </>
              ) : (
                <>
                  <strong>Insights not available yet</strong>
                  <p>
                    An administrator must generate the AI insights before
                    they become available to instructors.
                  </p>
                </>
              )}
            </div>
          )}

          {insight && (
            <div className="ai-insights-content">
              <div className="ai-insights-meta">
                <div>
                  <span>Sentiment</span>
                  <SentimentBadge
                    sentiment={insight.sentiment ?? 'neutral'}
                  />
                </div>

                {insight.human_reviewed && (
                  <span className="ai-insights-reviewed">
                    ✓ Human reviewed
                  </span>
                )}
              </div>

              {insight.summary && (
                <div className="ai-insights-block">
                  <span className="ai-insights-block__label">
                    SUMMARY
                  </span>
                  <p>{insight.summary}</p>
                </div>
              )}

              {insight.themes && insight.themes.length > 0 && (
                <div className="ai-insights-block">
                  <span className="ai-insights-block__label">
                    KEY THEMES
                  </span>

                  <ul>
                    {insight.themes.map((theme) => (
                      <li key={theme}>{theme}</li>
                    ))}
                  </ul>
                </div>
              )}

              {insight.improvement_areas &&
                insight.improvement_areas.length > 0 && (
                  <div className="ai-insights-block">
                    <span className="ai-insights-block__label">
                      SUGGESTED IMPROVEMENTS
                    </span>

                    <ul>
                      {insight.improvement_areas.map((area) => (
                        <li key={area}>{area}</li>
                      ))}
                    </ul>
                  </div>
                )}

              <div className="ai-insights-provider">
                Analysis provider:{' '}
                <strong>
                  {(insight.provider_used ?? 'unknown')
                    .replace(/_/g, ' ')}
                </strong>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  )
}

function SentimentBadge({
  sentiment,
}: {
  sentiment: string
}) {
  return (
    <span
      className={`ai-sentiment ai-sentiment--${sentiment.toLowerCase()}`}
    >
      {sentiment}
    </span>
  )
}

