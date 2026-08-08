/**
 * Student dashboard — shows enrolled courses, campaign status,
 * and links to the evaluation submission form.
 */
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import apiClient from '../lib/apiClient'
import { clearToken, getCurrentUser } from '../lib/auth'

interface CampaignStatus {
  campaign_id: string | null
  status: string | null
  has_submitted: boolean
}

interface EnrolledCourse {
  enrollment_id: string
  course_offering_id: string
  course_code: string
  course_name: string
  section_number: string
  semester_name: string
  instructor_name: string
  enrolled_at: string
  campaign: CampaignStatus | null
}

export default function StudentDashboard() {
  const navigate = useNavigate()
  const user = getCurrentUser()

  const { data: enrollments, isLoading, error } = useQuery<EnrolledCourse[]>({
    queryKey: ['my-enrollments'],
    queryFn: async () => {
      const resp = await apiClient.get<EnrolledCourse[]>('/me/enrollments')
      return resp.data
    },
  })

  function handleLogout() {
    clearToken()
    navigate('/login')
  }

  function getCampaignBadge(course: EnrolledCourse): React.ReactNode {
    const c = course.campaign
    if (!c || !c.status) return <span style={badge('gray')}>No evaluation</span>
    if (c.has_submitted) return <span style={badge('green')}>Submitted ✓</span>
    if (c.status === 'open') return <span style={badge('blue')}>Open — Awaiting submission</span>
    if (c.status === 'closed') return <span style={badge('gray')}>Closed</span>
    return <span style={badge('yellow')}>Draft</span>
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.h1}>Student Dashboard</h1>
          <p style={styles.subtitle}>{user?.email}</p>
        </div>
        <button onClick={handleLogout} style={styles.logoutBtn}>Sign out</button>
      </header>

      <main style={styles.main}>
        <h2 style={styles.h2}>My Enrolled Courses</h2>

        {isLoading && <p style={styles.muted}>Loading…</p>}
        {error && <p style={styles.errorText}>Failed to load enrollments.</p>}

        {!isLoading && enrollments?.length === 0 && (
          <p style={styles.muted}>You are not enrolled in any courses.</p>
        )}

        {enrollments && enrollments.length > 0 && (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Course</th>
                <th style={styles.th}>Section</th>
                <th style={styles.th}>Semester</th>
                <th style={styles.th}>Instructor</th>
                <th style={styles.th}>Evaluation</th>
                <th style={styles.th}>Action</th>
              </tr>
            </thead>
            <tbody>
              {enrollments.map((course) => (
                <tr key={course.enrollment_id} style={styles.tr}>
                  <td style={styles.td}>
                    <strong>{course.course_code}</strong> — {course.course_name}
                  </td>
                  <td style={styles.td}>{course.section_number}</td>
                  <td style={styles.td}>{course.semester_name}</td>
                  <td style={styles.td}>{course.instructor_name}</td>
                  <td style={styles.td}>{getCampaignBadge(course)}</td>
                  <td style={styles.td}>
                    {course.campaign?.status === 'open' && !course.campaign.has_submitted ? (
                      <button
                        style={styles.actionBtn}
                        onClick={() => navigate(`/student/submit/${course.campaign!.campaign_id}`)}
                      >
                        Submit Evaluation
                      </button>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </main>
    </div>
  )
}

function badge(color: string): React.CSSProperties {
  const colors: Record<string, { bg: string; text: string }> = {
    green: { bg: '#d1fae5', text: '#065f46' },
    blue: { bg: '#dbeafe', text: '#1e40af' },
    gray: { bg: '#f3f4f6', text: '#6b7280' },
    yellow: { bg: '#fef3c7', text: '#92400e' },
  }
  const c = colors[color] ?? colors.gray
  return {
    display: 'inline-block',
    padding: '2px 10px',
    borderRadius: '12px',
    fontSize: '0.8rem',
    fontWeight: 600,
    background: c.bg,
    color: c.text,
  }
}

const styles: Record<string, React.CSSProperties> = {
  page: { fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif', minHeight: '100vh', background: '#f7f8fa' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.25rem 2rem', background: '#fff', borderBottom: '1px solid #e5e7eb' },
  h1: { margin: 0, fontSize: '1.25rem', color: '#1f2328' },
  h2: { margin: '0 0 1rem', fontSize: '1.1rem', color: '#1f2328' },
  subtitle: { margin: '0.25rem 0 0', fontSize: '0.85rem', color: '#57606a' },
  main: { padding: '2rem', maxWidth: '1100px', margin: '0 auto' },
  muted: { color: '#57606a', fontSize: '0.9rem' },
  errorText: { color: '#c0392b', fontSize: '0.9rem' },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' },
  th: { padding: '0.75rem 1rem', textAlign: 'left', background: '#f7f8fa', fontSize: '0.85rem', fontWeight: 600, color: '#57606a', borderBottom: '1px solid #e5e7eb' },
  tr: { borderBottom: '1px solid #e5e7eb' },
  td: { padding: '0.75rem 1rem', fontSize: '0.9rem', color: '#1f2328' },
  logoutBtn: { padding: '0.4rem 1rem', background: 'transparent', border: '1px solid #e5e7eb', borderRadius: '6px', cursor: 'pointer', fontSize: '0.875rem' },
  actionBtn: { padding: '0.35rem 0.75rem', background: '#3b82d4', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.85rem' },
}
