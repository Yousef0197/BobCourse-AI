/**
 * Instructor dashboard — assigned campaigns, privacy-aware analytics,
 * response-threshold progress, and AI insights.
 */
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import apiClient from '../lib/apiClient'
import { clearToken, getCurrentUser } from '../lib/auth'
import AIInsightsPanel from '../components/AIInsightsPanel'
import Brand from '../components/Brand'

interface CourseOffering {
  id: string
  course_id: string
  semester_id: string
  instructor_id: string
  section_number: string
  capacity: number
}

interface Campaign {
  id: string
  course_offering_id: string
  status: string
  min_responses_threshold: number
}

interface CampaignStats {
  courseCode?: string
  courseName?: string
  overallAverage?: number
  responseRate?: number
  totalSubmissions?: number
  threshold?: number
  questionStats?: Array<{
    questionId: string
    questionText: string
    average: number
    distribution: Record<string, number>
  }>
}

export default function InstructorDashboard() {
  const navigate = useNavigate()
  const user = getCurrentUser()

  const {
    data: offerings,
    isLoading: loadingOfferings,
    error: offeringsError,
  } = useQuery<CourseOffering[]>({
    queryKey: ['course-offerings'],
    queryFn: async () => {
      const resp = await apiClient.get<CourseOffering[]>('/course-offerings')
      return resp.data
    },
  })

  const {
    data: campaigns,
    isLoading: loadingCampaigns,
    error: campaignsError,
  } = useQuery<Campaign[]>({
    queryKey: ['campaigns'],
    queryFn: async () => {
      const resp = await apiClient.get<Campaign[]>('/evaluation-campaigns')
      return resp.data
    },
  })

  function handleLogout() {
    clearToken()
    navigate('/login')
  }

  const myOfferings =
    offerings?.filter((offering) => offering.instructor_id === user?.userId) ?? []

  const myCampaigns =
    campaigns?.filter((campaign) =>
      myOfferings.some(
        (offering) => offering.id === campaign.course_offering_id,
      ),
    ) ?? []

  const openCampaigns = myCampaigns.filter(
    (campaign) => campaign.status === 'open',
  ).length

  const closedCampaigns = myCampaigns.filter(
    (campaign) => campaign.status === 'closed',
  ).length

  const draftCampaigns = myCampaigns.filter(
    (campaign) => campaign.status === 'draft',
  ).length

  const isLoading = loadingOfferings || loadingCampaigns
  const hasError = Boolean(offeringsError || campaignsError)

  return (
    <div className="instructor-page">
      <header className="instructor-topbar">
        <Brand compact />

        <div className="instructor-account">
          <div className="instructor-account__copy">
            <span className="instructor-account__role">Instructor</span>
            <span>{user?.email}</span>
          </div>

          <button
            type="button"
            className="bc-btn-secondary"
            onClick={handleLogout}
          >
            Sign out
          </button>
        </div>
      </header>

      <main className="instructor-main">
        <section className="instructor-welcome">
          <div>
            <span className="instructor-eyebrow">INSTRUCTOR WORKSPACE</span>
            <h1>Course evaluation insights</h1>
            <p>
              Review privacy-protected evaluation results, response progress,
              and AI-assisted insights for your assigned courses.
            </p>
          </div>
        </section>

        <section className="instructor-kpis">
          <article className="instructor-kpi">
            <span>Assigned offerings</span>
            <strong>{myOfferings.length}</strong>
            <small>Your current teaching assignments</small>
          </article>

          <article className="instructor-kpi">
            <span>Open campaigns</span>
            <strong>{openCampaigns}</strong>
            <small>Currently collecting responses</small>
          </article>

          <article className="instructor-kpi">
            <span>Results available</span>
            <strong>{closedCampaigns}</strong>
            <small>Closed evaluation campaigns</small>
          </article>

          <article className="instructor-kpi">
            <span>Preparing</span>
            <strong>{draftCampaigns}</strong>
            <small>Draft campaigns</small>
          </article>
        </section>

        <section className="instructor-privacy-note">
          <div className="instructor-privacy-note__icon" aria-hidden="true">
            ◈
          </div>

          <div>
            <strong>Privacy-protected results</strong>
            <p>
              Analytics remain unavailable until each campaign reaches its
              configured minimum-response threshold.
            </p>
          </div>
        </section>

        <section className="instructor-results">
          <div className="instructor-section-heading">
            <div>
              <span className="instructor-eyebrow">MY EVALUATIONS</span>
              <h2>Campaign results</h2>
            </div>

            <span className="instructor-campaign-count">
              {myCampaigns.length}{' '}
              {myCampaigns.length === 1 ? 'campaign' : 'campaigns'}
            </span>
          </div>

          {isLoading && (
            <div className="instructor-empty bc-card">
              <strong>Loading your evaluation campaigns…</strong>
              <span>Please wait a moment.</span>
            </div>
          )}

          {!isLoading && hasError && (
            <div className="instructor-error bc-card" role="alert">
              <strong>Unable to load your campaigns</strong>
              <span>Please refresh the page and try again.</span>
            </div>
          )}

          {!isLoading && !hasError && myCampaigns.length === 0 && (
            <div className="instructor-empty bc-card">
              <strong>No evaluation campaigns yet</strong>
              <span>
                Campaigns linked to your assigned courses will appear here.
              </span>
            </div>
          )}

          {!isLoading &&
            !hasError &&
            myCampaigns.map((campaign) => (
              <CampaignResultCard
                key={campaign.id}
                campaign={campaign}
              />
            ))}
        </section>
      </main>
    </div>
  )
}

function CampaignResultCard({ campaign }: { campaign: Campaign }) {
  const {
    data: stats,
    isLoading,
    error,
  } = useQuery<CampaignStats>({
    queryKey: ['campaign-stats', campaign.id],
    queryFn: async () => {
      const resp = await apiClient.get<CampaignStats>(
        `/analytics/campaigns/${campaign.id}/stats`,
      )
      return resp.data
    },
    enabled: campaign.status === 'closed',
    retry: false,
  })

  if (campaign.status !== 'closed') {
    const isOpen = campaign.status === 'open'

    return (
      <article className="instructor-campaign bc-card">
        <div className="instructor-campaign__header">
          <div>
            <span className="instructor-campaign__id">
              Campaign {campaign.id.slice(0, 8)}
            </span>
            <h3>
              {isOpen
                ? 'Evaluation in progress'
                : 'Evaluation campaign preparing'}
            </h3>
          </div>

          <StatusBadge status={campaign.status} />
        </div>

        <div className="instructor-guidance">
          <strong>
            {isOpen ? 'What happens next?' : 'Campaign status'}
          </strong>
          <p>
            {isOpen
              ? 'Student responses are currently being collected. Results become available after the campaign closes and the privacy threshold is satisfied.'
              : 'This campaign is still in draft status and is not collecting student responses yet.'}
          </p>
        </div>
      </article>
    )
  }

  if (isLoading) {
    return (
      <article className="instructor-campaign bc-card">
        <div className="instructor-loading">
          Loading campaign results…
        </div>
      </article>
    )
  }

  if (stats && typeof stats.threshold === 'number') {
    const totalSubmissions = stats.totalSubmissions ?? 0
    const threshold = campaign.min_responses_threshold
    const progress =
      threshold > 0
        ? Math.min(100, Math.round((totalSubmissions / threshold) * 100))
        : 0

    return (
      <article className="instructor-campaign bc-card">
        <div className="instructor-campaign__header">
          <div>
            <span className="instructor-campaign__id">
              Campaign {campaign.id.slice(0, 8)}
            </span>
            <h3>Results protected</h3>
          </div>

          <StatusBadge status="closed" />
        </div>

        <div className="instructor-threshold">
          <div className="instructor-threshold__top">
            <div>
              <span>Privacy threshold progress</span>
              <strong>
                {totalSubmissions} / {threshold} responses
              </strong>
            </div>

            <span>{progress}%</span>
          </div>

          <div
            className="instructor-threshold__bar"
            aria-label={`${progress}% of privacy threshold reached`}
          >
            <span style={{ width: `${progress}%` }} />
          </div>

          <p>
            Results remain hidden until at least {threshold} responses are
            collected to protect student anonymity.
          </p>
        </div>
      </article>
    )
  }

  if (error) {
    return (
      <article className="instructor-campaign bc-card">
        <div className="instructor-error-inline" role="alert">
          Failed to load analytics for this campaign.
        </div>
      </article>
    )
  }

  const questionStats = stats?.questionStats ?? []

  return (
    <article className="instructor-campaign bc-card">
      <div className="instructor-campaign__header">
        <div>
          <span className="instructor-campaign__id">
            CLOSED CAMPAIGN
          </span>

          <h3>
            {stats?.courseCode ?? 'Course'} —{' '}
            {stats?.courseName ?? 'Evaluation results'}
          </h3>
        </div>

        <StatusBadge status="closed" />
      </div>

      <div className="instructor-result-kpis">
        <ResultKPI
          label="Overall average"
          value={
            typeof stats?.overallAverage === 'number'
              ? stats.overallAverage.toFixed(2)
              : '—'
          }
        />

        <ResultKPI
          label="Response rate"
          value={
            typeof stats?.responseRate === 'number'
              ? `${stats.responseRate}%`
              : '—'
          }
        />

        <ResultKPI
          label="Submissions"
          value={String(stats?.totalSubmissions ?? '—')}
        />
      </div>

      <div className="instructor-question-block">
        <div className="instructor-question-heading">
          <span className="instructor-eyebrow">
            QUESTION BREAKDOWN
          </span>
          <h4>Per-question results</h4>
        </div>

        <div className="instructor-table-wrap">
          <table className="instructor-table">
            <thead>
              <tr>
                <th>Question</th>
                <th>Average</th>
                <th>1</th>
                <th>2</th>
                <th>3</th>
                <th>4</th>
                <th>5</th>
              </tr>
            </thead>

            <tbody>
              {questionStats.map((question) => (
                <tr key={question.questionId}>
                  <td>{question.questionText}</td>
                  <td>
                    <strong>{question.average.toFixed(2)}</strong>
                  </td>

                  {[1, 2, 3, 4, 5].map((rating) => (
                    <td key={rating}>
                      {question.distribution[rating] ?? 0}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <AIInsightsPanel campaignId={campaign.id} />
    </article>
  )
}

function ResultKPI({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="instructor-result-kpi">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`instructor-status instructor-status--${status}`}>
      {status}
    </span>
  )
}
