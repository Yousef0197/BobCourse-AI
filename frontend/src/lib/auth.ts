/**
 * Auth utilities — token storage and user info helpers.
 */

export type UserRole = 'admin' | 'instructor' | 'student'

export interface AuthUser {
  userId: string
  email: string
  role: UserRole
}

export function saveToken(token: string): void {
  localStorage.setItem('access_token', token)
  // Decode JWT payload (base64) to extract role
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    localStorage.setItem('user_role', payload.role ?? '')
    localStorage.setItem('user_email', payload.email ?? '')
    localStorage.setItem('user_id', payload.sub ?? '')
  } catch {
    // ignore parse errors
  }
}

export function clearToken(): void {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_role')
  localStorage.removeItem('user_email')
  localStorage.removeItem('user_id')
}

export function getToken(): string | null {
  return localStorage.getItem('access_token')
}

export function getCurrentUser(): AuthUser | null {
  const role = localStorage.getItem('user_role') as UserRole | null
  const email = localStorage.getItem('user_email')
  const userId = localStorage.getItem('user_id')
  if (!role || !email || !userId) return null
  return { userId, email, role }
}

export function isAuthenticated(): boolean {
  return getToken() !== null
}
