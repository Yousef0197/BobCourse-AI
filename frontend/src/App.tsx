/**
 * App routing — role-based navigation with auth guard.
 */
import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import StudentDashboard from './pages/StudentDashboard'
import SubmissionForm from './pages/SubmissionForm'
import InstructorDashboard from './pages/InstructorDashboard'
import AdminDashboard from './pages/AdminDashboard'
import { isAuthenticated, getCurrentUser } from './lib/auth'

/** Redirect to login if not authenticated, or to own dashboard if wrong role. */
function RequireRole({ role, children }: { role: string; children: React.ReactNode }) {
  if (!isAuthenticated()) return <Navigate to="/login" replace />
  const user = getCurrentUser()
  if (user?.role !== role) {
    // Redirect to correct dashboard based on actual role
    if (user?.role === 'admin') return <Navigate to="/admin" replace />
    if (user?.role === 'instructor') return <Navigate to="/instructor" replace />
    return <Navigate to="/student" replace />
  }
  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />

      {/* Student routes */}
      <Route
        path="/student"
        element={<RequireRole role="student"><StudentDashboard /></RequireRole>}
      />
      <Route
        path="/student/submit/:campaignId"
        element={<RequireRole role="student"><SubmissionForm /></RequireRole>}
      />

      {/* Instructor routes */}
      <Route
        path="/instructor"
        element={<RequireRole role="instructor"><InstructorDashboard /></RequireRole>}
      />

      {/* Admin routes */}
      <Route
        path="/admin"
        element={<RequireRole role="admin"><AdminDashboard /></RequireRole>}
      />

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App
