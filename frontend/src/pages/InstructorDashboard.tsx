/**
 * Instructor dashboard â€” assigned courses, evaluation results,
 * threshold enforcement message, AI insights panel.
 */
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import apiClient from '../lib/apiClient'
import { clearToken, getCurrentUser } from '../lib/auth'
import AIInsightsPanel from '../components/AIInsightsPanel'

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

export default function InstructorDashboard() {
  const navigate = useNavigate()
  const user = getCurrentUser()

  const { data: offerings, isLoading: loadingOfferings } = useQuery<CourseOffering[]>({
    queryKey: ['course-offerings'],
    queryFn: async () => {
      const resp = await apiClient.get<CourseOffering[]>('/course-offerings')
      return resp.data
    },
  })

  const { data: campaigns, isLoading: loadingCampaigns } = useQuery<Campaign[]>({
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

  // Filter to instructor's own offerings
  const myOfferings = offerings?.filter((o) => o.instructor_id === user?.userId) ?? []
  const myCampaigns = campaigns?.filter((c) =>
    myOfferings.some((o) => o.id === c.course_offering_id)
  ) ?? []

  const isLoading = loadingOfferings || loadingCampaigns

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.h1}>Instructor Dashboard</h1>
          <p style={styles.subtitle}>{user?.email}</p>
        </div>
        <button onClick={handleLogout} style={styles.logoutBtn}>Sign out</button>
      </header>

      <main style={styles.main}>
        <h2 style={styles.h2}>My Course Evaluations</h2>

        {isLoading && <p style={styles.muted}>Loadingâ€¦</p>}

        {!isLoading && myCampaigns.length === 0 && (
          <p style={styles.muted}>No evaluation campaigns found for your courses.</p>
        )}

        {myCampaigns.map((campaign) => (
          <CampaignResultCard
            key={campaign.id}
            campaign={campaign}
            userId={user?.userId ?? ''}
          />
        ))}
      </main>
    </div>
  )
}

function CampaignResultCard({ campaign }: { campaign: Campaign; userId: string }) {
  const { data: stats, isLoading, error } = useQuery<Record<string, unknown>>({
    queryKey: ['campaign-stats', campaign.id],
    queryFn: async () => {
      const resp = await apiClient.get<Record<string, unknown>>(`/analytics/campaigns/${campaign.id}/stats`)
      return resp.data
    },
    enabled: campaign.status === 'closed',
    retry: false,
  })

  if (campaign.status !== 'closed') {
    return (
      <div style={cardStyles.card}>
        <div style={cardStyles.header}>
          <strong>Campaign {campaign.id.slice(0, 8)}â€¦</strong>
          <StatusBadge status={campaign.status} />
        </div>
        <p style={cardStyles.muted}>Results will be available once the campaign is closed.</p>
      </div>
    )
  }

  if (isLoading) return <div style={cardStyles.card}><p style={cardStyles.muted}>Loading resultsâ€¦</p></div>

  // Threshold not met
  if (stats && 'threshold' in stats) {
    return (
      <div style={cardStyles.card}>
        <div style={cardStyles.header}>
          <strong>Campaign {campaign.id.slice(0, 8)}â€¦</strong>
          <StatusBadge status={campaign.status} />
        </div>
        <div style={cardStyles.thresholdNotice}>
          Results not yet available
          <p>
            Minimum {campaign.min_responses_threshold} responses required to protect student anonymity.
            Currently: {stats.totalSubmissions as number} response(s).
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={cardStyles.card}>
        <p style={{ color: '#c0392b', fontSize: '0.875rem' }}>Failed to load analytics.</p>
      </div>
    )
  }

  const questionStats = (stats?.questionStats as Array<{
    questionId: string
    questionText: string
    average: number
    distribution: Record<string, number>
  }>) ?? []

  return (
    <div style={cardStyles.card}>
      <div style={cardStyles.header}>
        <strong>{stats?.courseCode as string} â€” {stats?.courseName as string}</strong>
        <StatusBadge status={campaign.status} />
      </div>
      <div style={cardStyles.kpiRow}>
        <KPI label="Overall Average" value={(stats?.overallAverage as number)?.toFixed(2) ?? 'â€”'} />
        <KPI label="Response Rate" value={`${stats?.responseRate as number}%`} />
        <KPI label="Submissions" value={String(stats?.totalSubmissions ?? 'â€”')} />
      </div>

      <h4 style={cardStyles.subhead}>Per-Question Results</h4>
      <table style={cardStyles.table}>
        <thead>
          <tr>
            <th style={cardStyles.th}>Question</th>
            <th style={cardStyles.th}>Average</th>
            <th style={cardStyles.th}>1</th>
            <th style={cardStyles.th}>2</th>
            <th style={cardStyles.th}>3</th>
            <th style={cardStyles.th}>4</th>
            <th style={cardStyles.th}>5</th>
          </tr>
        </thead>
        <tbody>
          {questionStats.map((qs) => (
            <tr key={qs.questionId} style={cardStyles.tr}>
              <td style={cardStyles.td}>{qs.questionText}</td>
              <td style={{ ...cardStyles.td, fontWeight: 700 }}>{qs.average.toFixed(2)}</td>
              {[1, 2, 3, 4, 5].map((r) => (
                <td key={r} style={cardStyles.td}>{qs.distribution[r] ?? 0}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      <AIInsightsPanel campaignId={campaign.id} />
    </div>
  )
}

function KPI({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1f2328' }}>{value}</div>
      <div style={{ fontSize: '0.8rem', color: '#57606a' }}>{label}</div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, { bg: string; text: string }> = {
    open: { bg: '#d1fae5', text: '#065f46' },
    closed: { bg: '#f3f4f6', text: '#6b7280' },
    draft: { bg: '#fef3c7', text: '#92400e' },
  }
  const c = colors[status] ?? { bg: '#f3f4f6', text: '#6b7280' }
  return (
    <span style={{ padding: '2px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 600, background: c.bg, color: c.text }}>
      {status}
    </span>
  )
}

const styles: Record<string, React.CSSProperties> = {
  page: { fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif', minHeight: '100vh', background: '#f7f8fa' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.25rem 2rem', background: '#fff', borderBottom: '1px solid #e5e7eb' },
  h1: { margin: 0, fontSize: '1.25rem', color: '#1f2328' },
  h2: { margin: '0 0 1rem', fontSize: '1.1rem', color: '#1f2328' },
  subtitle: { margin: '0.25rem 0 0', fontSize: '0.85rem', color: '#57606a' },
  main: { padding: '2rem', maxWidth: '1000px', margin: '0 auto' },
  muted: { color: '#57606a', fontSize: '0.9rem' },
  logoutBtn: { padding: '0.4rem 1rem', background: 'transparent', border: '1px solid #e5e7eb', borderRadius: '6px', cursor: 'pointer', fontSize: '0.875rem' },
}

const cardStyles: Record<string, React.CSSProperties> = {
  card: { background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1.5rem', marginBottom: '1.5rem' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' },
  kpiRow: { display: 'flex', gap: '2rem', marginBottom: '1.5rem', padding: '1rem', background: '#f7f8fa', borderRadius: '6px' },
  subhead: { margin: '0 0 0.75rem', fontSize: '0.9rem', color: '#57606a', textTransform: 'uppercase', letterSpacing: '0.05em' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { padding: '0.5rem 0.75rem', textAlign: 'left', background: '#f7f8fa', fontSize: '0.8rem', fontWeight: 600, color: '#57606a', borderBottom: '1px solid #e5e7eb' },
  tr: { borderBottom: '1px solid #e5e7eb' },
  td: { padding: '0.5rem 0.75rem', fontSize: '0.875rem', color: '#1f2328' },
  muted: { color: '#57606a', fontSize: '0.875rem', margin: 0 },
  thresholdNotice: { background: '#fef3c7', border: '1px solid #f59e0b', borderRadius: '6px', padding: '1rem', fontSize: '0.875rem', color: '#92400e' },
}

