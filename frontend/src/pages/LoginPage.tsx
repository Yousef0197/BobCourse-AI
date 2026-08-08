/**
 * Login page for admin, instructor, and student roles.
 * Demo cards only prefill credentials; authentication still uses the normal API.
 */
import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../lib/apiClient'
import { getCurrentUser, saveToken } from '../lib/auth'
import Brand from '../components/Brand'

const demoAccounts = [
  {
    role: 'Student',
    email: 'student@bobcourse.edu',
    password: 'Student1234!',
    description: 'Submit course evaluations and track completion.',
  },
  {
    role: 'Instructor',
    email: 'instructor@bobcourse.edu',
    password: 'Instructor1234!',
    description: 'Review anonymous course feedback and insights.',
  },
  {
    role: 'Admin',
    email: 'admin@bobcourse.edu',
    password: 'Admin1234!',
    description: 'Manage campaigns, users, analytics, and reports.',
  },
]

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  function selectDemo(account: (typeof demoAccounts)[number]) {
    setEmail(account.email)
    setPassword(account.password)
    setError(null)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const resp = await apiClient.post<{
        access_token: string
        token_type: string
      }>('/auth/login', {
        email,
        password,
      })

      saveToken(resp.data.access_token)

      const user = getCurrentUser()

      if (user?.role === 'admin') navigate('/admin')
      else if (user?.role === 'instructor') navigate('/instructor')
      else navigate('/student')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status: number } }

      if (axiosErr.response?.status === 401) {
        setError('Invalid email or password.')
      } else {
        setError('Login failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="login-shell">
      <section className="login-hero">
        <Brand
          subtitle="University Course Evaluation Intelligence"
        />

        <div className="login-hero__content">
          <span className="login-eyebrow">ACADEMIC INTELLIGENCE PLATFORM</span>

          <h1>
            Better feedback.
            <br />
            Better courses.
          </h1>

          <p>
            A secure course-evaluation platform combining anonymous student
            feedback, academic analytics, and responsible AI insights.
          </p>

          <div className="login-feature-grid">
            <div>
              <strong>Private by design</strong>
              <span>Response thresholds protect student anonymity.</span>
            </div>

            <div>
              <strong>Actionable analytics</strong>
              <span>Turn evaluation results into useful academic signals.</span>
            </div>

            <div>
              <strong>Responsible AI</strong>
              <span>PII masking, transparent providers, and human review.</span>
            </div>
          </div>
        </div>

        <div className="login-hero__footer">
          BobCourse AI · Course Evaluation Intelligence
        </div>
      </section>

      <section className="login-panel">
        <div className="login-card">
          <div className="login-mobile-brand">
            <Brand />
          </div>

          <div className="login-heading">
            <span className="login-kicker">WELCOME BACK</span>
            <h2>Sign in to BobCourse AI</h2>
            <p>Access your university course evaluation workspace.</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <label>
              <span>Email address</span>
              <input
                className="bc-input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@university.edu"
                autoComplete="email"
              />
            </label>

            <label>
              <span>Password</span>
              <input
                className="bc-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                autoComplete="current-password"
              />
            </label>

            {error && (
              <div className="login-error" role="alert">
                {error}
              </div>
            )}

            <button
              className="bc-btn-primary login-submit"
              type="submit"
              disabled={loading}
            >
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

          <div className="login-divider">
            <span>Demo accounts</span>
          </div>

          <div className="demo-grid">
            {demoAccounts.map((account) => {
              const selected =
                email === account.email && password === account.password

              return (
                <button
                  key={account.role}
                  type="button"
                  className={`demo-account${selected ? ' demo-account--selected' : ''}`}
                  onClick={() => selectDemo(account)}
                >
                  <span className="demo-account__role">
                    {account.role}
                  </span>

                  <span className="demo-account__description">
                    {account.description}
                  </span>

                  <span className="demo-account__action">
                    {selected ? 'Selected ✓' : 'Use demo →'}
                  </span>
                </button>
              )
            })}
          </div>

          <p className="demo-notice">
            Demo credentials are provided for local evaluation only and must
            not be used in production.
          </p>
        </div>
      </section>
    </main>
  )
}
