/**
 * Student dashboard — enrolled courses, evaluation progress, and next actions.
 */
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import apiClient from '../lib/apiClient'
import { clearToken, getCurrentUser } from '../lib/auth'
import Brand from '../components/Brand'

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

  const {
    data: enrollments,
    isLoading,
    error,
  } = useQuery<EnrolledCourse[]>({
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

  const courses = enrollments ?? []

  const submittedCount = courses.filter(
    (course) => course.campaign?.has_submitted,
  ).length

  const pendingCourses = courses.filter(
    (course) =>
      course.campaign?.status === 'open' &&
      !course.campaign.has_submitted,
  )

  const completionRate =
    courses.length > 0
      ? Math.round((submittedCount / courses.length) * 100)
      : 0

  const nextCourse = pendingCourses[0]

  function campaignMeta(course: EnrolledCourse) {
    const campaign = course.campaign

    if (!campaign?.status) {
      return {
        label: 'Not available',
        tone: 'neutral',
        guidance: 'No evaluation campaign has been published yet.',
      }
    }

    if (campaign.has_submitted) {
      return {
        label: 'Submitted',
        tone: 'success',
        guidance: 'Your evaluation has been received successfully.',
      }
    }

    if (campaign.status === 'open') {
      return {
        label: 'Action required',
        tone: 'attention',
        guidance: 'Evaluation is open and waiting for your response.',
      }
    }

    if (campaign.status === 'closed') {
      return {
        label: 'Closed',
        tone: 'neutral',
        guidance: 'This evaluation period has ended.',
      }
    }

    return {
      label: 'Coming soon',
      tone: 'draft',
      guidance: 'The evaluation campaign is still being prepared.',
    }
  }

  return (
    <div className="student-page">
      <header className="student-topbar">
        <Brand compact />

        <div className="student-account">
          <div className="student-account__copy">
            <span className="student-account__role">Student</span>
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

      <main className="student-main">
        <section className="student-welcome">
          <div>
            <span className="student-eyebrow">STUDENT WORKSPACE</span>
            <h1>Course evaluations</h1>
            <p>
              Review your enrolled courses, complete available evaluations,
              and keep track of your submission progress.
            </p>
          </div>

          {nextCourse?.campaign?.campaign_id && (
            <button
              type="button"
              className="bc-btn-primary student-primary-action"
              onClick={() =>
                navigate(
                  `/student/submit/${nextCourse.campaign!.campaign_id}`,
                )
              }
            >
              Complete next evaluation →
            </button>
          )}
        </section>

        <section className="student-kpis">
          <article className="student-kpi">
            <span>Enrolled courses</span>
            <strong>{courses.length}</strong>
            <small>Current course list</small>
          </article>

          <article className="student-kpi">
            <span>Submitted</span>
            <strong>{submittedCount}</strong>
            <small>Completed evaluations</small>
          </article>

          <article className="student-kpi">
            <span>Action required</span>
            <strong>{pendingCourses.length}</strong>
            <small>Open evaluations remaining</small>
          </article>

          <article className="student-kpi student-kpi--progress">
            <span>Completion</span>
            <strong>{completionRate}%</strong>

            <div
              className="student-progress"
              aria-label={`${completionRate}% evaluation completion`}
            >
              <span style={{ width: `${completionRate}%` }} />
            </div>
          </article>
        </section>

        {pendingCourses.length > 0 && (
          <section className="student-next-action">
            <div className="student-next-action__icon" aria-hidden="true">
              ✓
            </div>

            <div>
              <span>Next recommended action</span>
              <strong>
                Complete {nextCourse.course_code} — {nextCourse.course_name}
              </strong>
              <p>
                This evaluation is currently open. Your response is submitted
                anonymously to the course evaluation system.
              </p>
            </div>
          </section>
        )}

        <section className="student-course-section bc-card">
          <div className="student-section-heading">
            <div>
              <span className="student-eyebrow">MY COURSES</span>
              <h2>Enrolled courses</h2>
            </div>

            <span className="student-course-count">
              {courses.length} {courses.length === 1 ? 'course' : 'courses'}
            </span>
          </div>

          {isLoading && (
            <div className="student-empty-state">
              <strong>Loading your courses…</strong>
              <span>Please wait a moment.</span>
            </div>
          )}

          {error && (
            <div className="student-error-state" role="alert">
              <strong>Unable to load enrollments</strong>
              <span>Please refresh the page and try again.</span>
            </div>
          )}

          {!isLoading && !error && courses.length === 0 && (
            <div className="student-empty-state">
              <strong>No enrolled courses yet</strong>
              <span>
                Courses assigned to your account will appear here.
              </span>
            </div>
          )}

          {courses.length > 0 && (
            <div className="student-table-wrap">
              <table className="student-table">
                <thead>
                  <tr>
                    <th>Course</th>
                    <th>Section</th>
                    <th>Semester</th>
                    <th>Instructor</th>
                    <th>Evaluation</th>
                    <th>Next step</th>
                  </tr>
                </thead>

                <tbody>
                  {courses.map((course) => {
                    const meta = campaignMeta(course)

                    return (
                      <tr key={course.enrollment_id}>
                        <td>
                          <div className="student-course-name">
                            <strong>{course.course_code}</strong>
                            <span>{course.course_name}</span>
                          </div>
                        </td>

                        <td>{course.section_number}</td>
                        <td>{course.semester_name}</td>
                        <td>{course.instructor_name}</td>

                        <td>
                          <span
                            className={`student-status student-status--${meta.tone}`}
                          >
                            {meta.label}
                          </span>
                        </td>

                        <td>
                          {course.campaign?.status === 'open' &&
                          !course.campaign.has_submitted &&
                          course.campaign.campaign_id ? (
                            <button
                              type="button"
                              className="student-row-action"
                              onClick={() =>
                                navigate(
                                  `/student/submit/${course.campaign!.campaign_id}`,
                                )
                              }
                            >
                              Submit evaluation
                            </button>
                          ) : (
                            <span className="student-guidance">
                              {meta.guidance}
                            </span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
