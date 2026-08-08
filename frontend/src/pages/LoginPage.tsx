/**
 * Login page — handles all three roles (admin, instructor, student).
 * On success, stores JWT and redirects to role-appropriate dashboard.
 */
import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../lib/apiClient'
import { saveToken, getCurrentUser } from '../lib/auth'

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const resp = await apiClient.post<{ access_token: string; token_type: string }>('/auth/login', {
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
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>BobCourse-AI</h1>
        <p style={styles.subtitle}>University Course Evaluation System</p>
        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={styles.input}
              placeholder="you@university.edu"
              autoComplete="email"
            />
          </label>
          <label style={styles.label}>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={styles.input}
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </label>
          {error && <p style={styles.error}>{error}</p>}
          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
        <p style={styles.demo}>
          Demo: admin@bobcourse.edu / Admin1234!
        </p>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#f7f8fa',
    fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif',
  },
  card: {
    background: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '2.5rem',
    width: '100%',
    maxWidth: '420px',
  },
  title: { margin: '0 0 0.25rem', fontSize: '1.5rem', color: '#1f2328' },
  subtitle: { margin: '0 0 1.5rem', fontSize: '0.9rem', color: '#57606a' },
  form: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  label: { display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.9rem', color: '#1f2328' },
  input: {
    padding: '0.5rem 0.75rem',
    border: '1px solid #e5e7eb',
    borderRadius: '6px',
    fontSize: '1rem',
    outline: 'none',
  },
  error: { margin: 0, color: '#c0392b', fontSize: '0.875rem' },
  button: {
    padding: '0.625rem',
    background: '#3b82d4',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    fontSize: '1rem',
    cursor: 'pointer',
    marginTop: '0.5rem',
  },
  demo: { marginTop: '1.5rem', fontSize: '0.8rem', color: '#57606a', textAlign: 'center' },
}
