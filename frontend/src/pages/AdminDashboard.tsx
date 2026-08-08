/**
 * Admin Dashboard — full sidebar navigation with all management sections.
 * Sections: Dashboard, Campaigns, Academic Structure, Users, Templates, Analytics, Reports
 */
import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../lib/apiClient'
import { clearToken, getCurrentUser } from '../lib/auth'
import AIInsightsPanel from '../components/AIInsightsPanel'
import Brand from '../components/Brand'

// ─── Types ───────────────────────────────────────────────────────────────────

type Section =
  | 'dashboard'
  | 'campaigns'
  | 'structure'
  | 'users'
  | 'templates'
  | 'analytics'
  | 'reports'

interface College { id: string; name: string; code: string }
interface Department { id: string; name: string; code: string; college_id: string }
interface Course { id: string; code: string; name: string; credit_hours: number; department_id: string }
interface Semester { id: string; name: string; year: number; season: string; is_active: boolean }
interface CourseOfferingEnriched {
  id: string; section_number: string; capacity: number
  course_code: string; course_name: string; course_id: string
  semester_name: string; semester_id: string
  instructor_name: string; instructor_id: string
  enrolled_count: number
  campaign_id: string | null; campaign_status: string | null
}
interface CampaignOverview {
  id: string; status: string; course_code: string; course_name: string
  semester_name: string; instructor_name: string; section_number: string
  submission_count: number; enrolled_count: number
  min_responses_threshold: number; created_at: string
  opens_at: string | null; closes_at: string | null
  course_offering_id: string; template_id: string
}
interface AdminStats {
  totalStudents: number; totalInstructors: number; totalAdmins: number
  totalCourses: number; totalColleges: number; totalDepartments: number
}
interface DashboardKPI {
  totalCampaigns: number; activeCampaigns: number; totalSubmissions: number
  averageRating: number; overallResponseRate: number
}
interface AdminUser {
  id: string; email: string; full_name: string; role: string
  is_active: boolean; department_name: string | null; created_at: string
}
interface EvalTemplate { id: string; name: string; description: string; is_active: boolean }
interface EvalQuestion { id: string; text: string; order_index: number; is_required: boolean }

// ─── Main Component ───────────────────────────────────────────────────────────

export default function AdminDashboard() {
  const navigate = useNavigate()
  const user = getCurrentUser()
  const [section, setSection] = useState<Section>('dashboard')

  function handleLogout() {
    clearToken()
    navigate('/login')
  }

  const navItems: Array<{ id: Section; label: string; icon: string }> = [
    { id: 'dashboard', label: 'Dashboard', icon: '▣' },
    { id: 'campaigns', label: 'Campaigns', icon: '◷' },
    { id: 'structure', label: 'Academic Structure', icon: '⊞' },
    { id: 'users', label: 'Users', icon: '⊙' },
    { id: 'templates', label: 'Templates', icon: '☰' },
    { id: 'analytics', label: 'Analytics', icon: '◈' },
    { id: 'reports', label: 'Reports', icon: '↓' },
  ]

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="admin-sidebar__brand">
          <Brand subtitle="Admin Console" />
        </div>

        <div className="admin-sidebar__label">
          MANAGEMENT
        </div>

        <nav className="admin-sidebar__nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setSection(item.id)}
              className={`admin-nav-item${
                section === item.id ? ' admin-nav-item--active' : ''
              }`}
            >
              <span className="admin-nav-item__icon">
                {item.icon}
              </span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="admin-sidebar__footer">
          <div className="admin-sidebar__user">
            <span className="admin-sidebar__role">
              Administrator
            </span>
            <span title={user?.email}>
              {user?.email}
            </span>
          </div>

          <button
            type="button"
            className="admin-sidebar__logout"
            onClick={handleLogout}
          >
            Sign out
          </button>
        </div>
      </aside>

      <div className="admin-workspace">
        <header className="admin-header">
          <div>
            <span className="admin-header__eyebrow">
              ADMIN CONSOLE
            </span>

            <h1>
              {navItems.find((item) => item.id === section)?.label}
            </h1>
          </div>

          <div className="admin-header__status">
            <span />
            System workspace
          </div>
        </header>

        <main className="admin-content">
          {section === 'dashboard' && <DashboardSection />}
          {section === 'campaigns' && <CampaignsSection />}
          {section === 'structure' && <AcademicStructureSection />}
          {section === 'users' && <UsersSection />}
          {section === 'templates' && <TemplatesSection />}
          {section === 'analytics' && <AnalyticsSection />}
          {section === 'reports' && <ReportsSection />}
        </main>
      </div>
    </div>
  )
}

// ─── Dashboard Section ────────────────────────────────────────────────────────

function DashboardSection() {
  const { data: stats } = useQuery<AdminStats>({
    queryKey: ['admin-stats'],
    queryFn: async () => (await apiClient.get<AdminStats>('/admin/stats')).data,
  })
  const { data: kpis, isLoading: kpisLoading, error: kpisError } = useQuery<DashboardKPI>({
    queryKey: ['dashboard-kpis'],
    queryFn: async () => (await apiClient.get<DashboardKPI>('/analytics/dashboard')).data,
    retry: false,
  })
  const { data: campaigns } = useQuery<CampaignOverview[]>({
    queryKey: ['campaigns-overview'],
    queryFn: async () => (await apiClient.get<CampaignOverview[]>('/admin/campaigns/overview')).data,
  })

  const recentCampaigns = campaigns?.slice(0, 5) ?? []
  const openCount = campaigns?.filter((c) => c.status === 'open').length ?? 0

  return (
    <div>
      {/* KPI row 1 — from Java analytics */}
      <SectionTitle>Evaluation Overview</SectionTitle>
      {kpisLoading && <p style={s.muted}>Loading analytics…</p>}
      {kpisError && <InfoBox type="warning">Analytics service unavailable — KPIs cannot be computed right now.</InfoBox>}
      {kpis && (
        <div style={s.kpiGrid}>
          <KPICard label="Total Campaigns" value={kpis.totalCampaigns} color="#3b82d4" />
          <KPICard label="Active Campaigns" value={kpis.activeCampaigns} color="#16a34a" />
          <KPICard label="Total Submissions" value={kpis.totalSubmissions} color="#7c3aed" />
          <KPICard label="Avg Rating" value={kpis.averageRating > 0 ? kpis.averageRating.toFixed(2) : '—'} color="#d97706" />
          <KPICard label="Response Rate" value={`${kpis.overallResponseRate ?? 0}%`} color="#0891b2" />
        </div>
      )}

      {/* KPI row 2 — from admin stats */}
      {stats && (
        <>
          <SectionTitle>Academic Structure</SectionTitle>
          <div style={s.kpiGrid}>
            <KPICard label="Colleges" value={stats.totalColleges} />
            <KPICard label="Departments" value={stats.totalDepartments} />
            <KPICard label="Courses" value={stats.totalCourses} />
            <KPICard label="Students" value={stats.totalStudents} />
            <KPICard label="Instructors" value={stats.totalInstructors} />
          </div>
        </>
      )}

      {/* Recent campaigns */}
      {recentCampaigns.length > 0 && (
        <>
          <SectionTitle>Recent Campaigns</SectionTitle>
          <CampaignTable campaigns={recentCampaigns} showActions={false} />
        </>
      )}

      {openCount > 0 && (
        <InfoBox type="info">{openCount} campaign{openCount !== 1 ? 's' : ''} currently open for student submissions.</InfoBox>
      )}
    </div>
  )
}

// ─── Campaigns Section ────────────────────────────────────────────────────────

function CampaignsSection() {
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)

  const { data: campaigns, isLoading } = useQuery<CampaignOverview[]>({
    queryKey: ['campaigns-overview'],
    queryFn: async () => (await apiClient.get<CampaignOverview[]>('/admin/campaigns/overview')).data,
  })
  const { data: offerings } = useQuery<CourseOfferingEnriched[]>({
    queryKey: ['offerings-enriched'],
    queryFn: async () => (await apiClient.get<CourseOfferingEnriched[]>('/admin/course-offerings/enriched')).data,
  })
  const { data: templates } = useQuery<EvalTemplate[]>({
    queryKey: ['templates'],
    queryFn: async () => (await apiClient.get<EvalTemplate[]>('/evaluation-templates')).data,
  })

  // Offerings that don't already have a campaign
  const availableOfferings = offerings?.filter((o) => !o.campaign_id) ?? []

  const openCampaign = useMutation({
    mutationFn: (id: string) => apiClient.put(`/evaluation-campaigns/${id}`, { status: 'open' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns-overview'] }),
  })
  const closeCampaign = useMutation({
    mutationFn: (id: string) => apiClient.put(`/evaluation-campaigns/${id}`, { status: 'closed' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns-overview'] }),
  })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <SectionTitle style={{ margin: 0 }}>Evaluation Campaigns</SectionTitle>
        <button style={s.primaryBtn} onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? 'Cancel' : '+ New Campaign'}
        </button>
      </div>

      {showCreate && (
        <CreateCampaignForm
          offerings={availableOfferings}
          templates={templates ?? []}
          onSuccess={() => { setShowCreate(false); qc.invalidateQueries({ queryKey: ['campaigns-overview'] }) }}
        />
      )}

      {isLoading && <p style={s.muted}>Loading campaigns…</p>}
      {!isLoading && campaigns?.length === 0 && (
        <EmptyState message="No campaigns yet. Create one by selecting a course offering and template." />
      )}
      {campaigns && campaigns.length > 0 && (
        <CampaignTable
          campaigns={campaigns}
          showActions
          onOpen={(id) => { if (window.confirm('Open this campaign for student submissions?')) openCampaign.mutate(id) }}
          onClose={(id) => { if (window.confirm('Close this campaign? Students will no longer be able to submit.')) closeCampaign.mutate(id) }}
        />
      )}
    </div>
  )
}

function CreateCampaignForm({ offerings, templates, onSuccess }: {
  offerings: CourseOfferingEnriched[]; templates: EvalTemplate[]; onSuccess: () => void
}) {
  const [offeringId, setOfferingId] = useState('')
  const [templateId, setTemplateId] = useState('')
  const [threshold, setThreshold] = useState(3)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!offeringId || !templateId) { setError('Please select a course offering and template.'); return }
    setError(null)
    try {
      await apiClient.post('/evaluation-campaigns', {
        course_offering_id: offeringId,
        template_id: templateId,
        status: 'draft',
        min_responses_threshold: threshold,
      })
      onSuccess()
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      setError(e.response?.data?.detail ?? 'Failed to create campaign.')
    }
  }

  return (
    <div style={s.formCard}>
      <h3 style={s.formTitle}>Create New Campaign</h3>
      <form onSubmit={handleSubmit}>
        <FormField label="Course Offering">
          <select value={offeringId} onChange={(e) => setOfferingId(e.target.value)} style={s.input}>
            <option value="">— Select course offering —</option>
            {offerings.map((o) => (
              <option key={o.id} value={o.id}>
                {o.course_code} — {o.course_name} / {o.semester_name} / Sec {o.section_number} ({o.instructor_name})
              </option>
            ))}
          </select>
        </FormField>
        <FormField label="Evaluation Template">
          <select value={templateId} onChange={(e) => setTemplateId(e.target.value)} style={s.input}>
            <option value="">— Select template —</option>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
        </FormField>
        <FormField label={`Min. Response Threshold (${threshold})`}>
          <input type="range" min={1} max={20} value={threshold} onChange={(e) => setThreshold(Number(e.target.value))} style={{ width: '100%' }} />
          <span style={s.helpText}>Results hidden from instructor until {threshold} responses received.</span>
        </FormField>
        {error && <p style={s.errorText}>{error}</p>}
        <div style={s.formActions}>
          <button type="submit" style={s.primaryBtn}>Save as Draft</button>
        </div>
      </form>
    </div>
  )
}

function CampaignTable({ campaigns, showActions, onOpen, onClose }: {
  campaigns: CampaignOverview[]
  showActions: boolean
  onOpen?: (id: string) => void
  onClose?: (id: string) => void
}) {
  return (
    <table style={s.table}>
      <thead>
        <tr>
          <th style={s.th}>Course</th>
          <th style={s.th}>Semester</th>
          <th style={s.th}>Instructor</th>
          <th style={s.th}>Status</th>
          <th style={s.th}>Submissions</th>
          <th style={s.th}>Response Rate</th>
          {showActions && <th style={s.th}>Actions</th>}
        </tr>
      </thead>
      <tbody>
        {campaigns.map((c) => {
          const rate = c.enrolled_count > 0 ? Math.round(c.submission_count / c.enrolled_count * 100) : 0
          return (
            <tr key={c.id} style={s.tr}>
              <td style={s.td}><strong>{c.course_code}</strong> {c.course_name}</td>
              <td style={s.td}>{c.semester_name}</td>
              <td style={s.td}>{c.instructor_name}</td>
              <td style={s.td}><StatusBadge status={c.status} /></td>
              <td style={s.td}>{c.submission_count} / {c.enrolled_count}</td>
              <td style={s.td}>{rate}%</td>
              {showActions && (
                <td style={s.td}>
                  {c.status === 'draft' && onOpen && (
                    <button style={s.actionBtnGreen} onClick={() => onOpen(c.id)}>Open</button>
                  )}
                  {c.status === 'open' && onClose && (
                    <button style={s.actionBtnRed} onClick={() => onClose(c.id)}>Close</button>
                  )}
                  {c.status === 'closed' && (
                    <span style={s.closedLabel}>Closed</span>
                  )}
                </td>
              )}
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}

// ─── Academic Structure Section ───────────────────────────────────────────────

function AcademicStructureSection() {
  const [tab, setTab] = useState<'colleges' | 'departments' | 'courses' | 'semesters' | 'offerings'>('colleges')
  const tabs: Array<{ id: typeof tab; label: string }> = [
    { id: 'colleges', label: 'Colleges' },
    { id: 'departments', label: 'Departments' },
    { id: 'courses', label: 'Courses' },
    { id: 'semesters', label: 'Semesters' },
    { id: 'offerings', label: 'Course Offerings' },
  ]

  return (
    <div>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {tabs.map((t) => (
          <button key={t.id} style={tab === t.id ? s.subTabActive : s.subTab} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>
      {tab === 'colleges' && <CollegesTab />}
      {tab === 'departments' && <DepartmentsTab />}
      {tab === 'courses' && <CoursesTab />}
      {tab === 'semesters' && <SemestersTab />}
      {tab === 'offerings' && <OfferingsTab />}
    </div>
  )
}

function CollegesTab() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState(''); const [code, setCode] = useState(''); const [err, setErr] = useState<string | null>(null)

  const { data: colleges, isLoading } = useQuery<College[]>({
    queryKey: ['colleges'],
    queryFn: async () => (await apiClient.get<College[]>('/colleges')).data,
  })

  async function handleCreate(e: FormEvent) {
    e.preventDefault(); setErr(null)
    try {
      await apiClient.post('/colleges', { name, code })
      qc.invalidateQueries({ queryKey: ['colleges'] }); setShowForm(false); setName(''); setCode('')
    } catch (ex: unknown) {
      setErr((ex as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Failed.')
    }
  }

  return (
    <div>
      <StructureHeader title="Colleges" onAdd={() => setShowForm(!showForm)} />
      {showForm && (
        <div style={s.formCard}>
          <form onSubmit={handleCreate} style={s.inlineForm}>
            <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} style={s.input} required />
            <input placeholder="Code (e.g. COE)" value={code} onChange={(e) => setCode(e.target.value)} style={s.input} required />
            <button type="submit" style={s.primaryBtn}>Add</button>
            {err && <span style={s.errorText}>{err}</span>}
          </form>
        </div>
      )}
      {isLoading ? <p style={s.muted}>Loading…</p> : (
        <table style={s.table}>
          <thead><tr><th style={s.th}>Name</th><th style={s.th}>Code</th></tr></thead>
          <tbody>
            {colleges?.map((c) => (
              <tr key={c.id} style={s.tr}>
                <td style={s.td}>{c.name}</td>
                <td style={s.td}><code>{c.code}</code></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {!isLoading && colleges?.length === 0 && <EmptyState message="No colleges yet." />}
    </div>
  )
}

function DepartmentsTab() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState(''); const [code, setCode] = useState(''); const [collegeId, setCollegeId] = useState(''); const [err, setErr] = useState<string | null>(null)

  const { data: depts } = useQuery<Department[]>({ queryKey: ['departments'], queryFn: async () => (await apiClient.get<Department[]>('/departments')).data })
  const { data: colleges } = useQuery<College[]>({ queryKey: ['colleges'], queryFn: async () => (await apiClient.get<College[]>('/colleges')).data })

  const collegeMap = Object.fromEntries((colleges ?? []).map((c) => [c.id, c.name]))

  async function handleCreate(e: FormEvent) {
    e.preventDefault(); setErr(null)
    try {
      await apiClient.post('/departments', { name, code, college_id: collegeId })
      qc.invalidateQueries({ queryKey: ['departments'] }); setShowForm(false); setName(''); setCode(''); setCollegeId('')
    } catch (ex: unknown) { setErr((ex as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Failed.') }
  }

  return (
    <div>
      <StructureHeader title="Departments" onAdd={() => setShowForm(!showForm)} />
      {showForm && (
        <div style={s.formCard}>
          <form onSubmit={handleCreate} style={s.inlineForm}>
            <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} style={s.input} required />
            <input placeholder="Code (e.g. CS)" value={code} onChange={(e) => setCode(e.target.value)} style={s.input} required />
            <select value={collegeId} onChange={(e) => setCollegeId(e.target.value)} style={s.input} required>
              <option value="">— College —</option>
              {colleges?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <button type="submit" style={s.primaryBtn}>Add</button>
            {err && <span style={s.errorText}>{err}</span>}
          </form>
        </div>
      )}
      <table style={s.table}>
        <thead><tr><th style={s.th}>Name</th><th style={s.th}>Code</th><th style={s.th}>College</th></tr></thead>
        <tbody>
          {depts?.map((d) => (
            <tr key={d.id} style={s.tr}>
              <td style={s.td}>{d.name}</td>
              <td style={s.td}><code>{d.code}</code></td>
              <td style={s.td}>{collegeMap[d.college_id] ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function CoursesTab() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [code, setCode] = useState(''); const [name, setName] = useState(''); const [credits, setCredits] = useState(3); const [deptId, setDeptId] = useState(''); const [err, setErr] = useState<string | null>(null)

  const { data: courses } = useQuery<Course[]>({ queryKey: ['courses'], queryFn: async () => (await apiClient.get<Course[]>('/courses')).data })
  const { data: depts } = useQuery<Department[]>({ queryKey: ['departments'], queryFn: async () => (await apiClient.get<Department[]>('/departments')).data })

  const deptMap = Object.fromEntries((depts ?? []).map((d) => [d.id, d.name]))

  async function handleCreate(e: FormEvent) {
    e.preventDefault(); setErr(null)
    try {
      await apiClient.post('/courses', { code, name, credit_hours: credits, department_id: deptId })
      qc.invalidateQueries({ queryKey: ['courses'] }); setShowForm(false); setCode(''); setName(''); setDeptId('')
    } catch (ex: unknown) { setErr((ex as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Failed.') }
  }

  return (
    <div>
      <StructureHeader title="Courses" onAdd={() => setShowForm(!showForm)} />
      {showForm && (
        <div style={s.formCard}>
          <form onSubmit={handleCreate} style={s.inlineForm}>
            <input placeholder="Code (e.g. CS101)" value={code} onChange={(e) => setCode(e.target.value)} style={s.input} required />
            <input placeholder="Course name" value={name} onChange={(e) => setName(e.target.value)} style={{ ...s.input, minWidth: '220px' }} required />
            <input type="number" min={1} max={6} value={credits} onChange={(e) => setCredits(Number(e.target.value))} style={{ ...s.input, width: '80px' }} placeholder="Credits" />
            <select value={deptId} onChange={(e) => setDeptId(e.target.value)} style={s.input} required>
              <option value="">— Department —</option>
              {depts?.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
            <button type="submit" style={s.primaryBtn}>Add</button>
            {err && <span style={s.errorText}>{err}</span>}
          </form>
        </div>
      )}
      <table style={s.table}>
        <thead><tr><th style={s.th}>Code</th><th style={s.th}>Name</th><th style={s.th}>Credits</th><th style={s.th}>Department</th></tr></thead>
        <tbody>
          {courses?.map((c) => (
            <tr key={c.id} style={s.tr}>
              <td style={s.td}><code>{c.code}</code></td>
              <td style={s.td}>{c.name}</td>
              <td style={s.td}>{c.credit_hours}h</td>
              <td style={s.td}>{deptMap[c.department_id] ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function SemestersTab() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [semName, setSemName] = useState(''); const [season, setSeason] = useState('fall'); const [year, setYear] = useState(new Date().getFullYear()); const [err, setErr] = useState<string | null>(null)

  const { data: semesters } = useQuery<Semester[]>({ queryKey: ['semesters'], queryFn: async () => (await apiClient.get<Semester[]>('/semesters')).data })

  async function handleCreate(e: FormEvent) {
    e.preventDefault(); setErr(null)
    const startDate = season === 'fall' ? `${year}-09-01` : season === 'spring' ? `${year}-01-15` : `${year}-06-01`
    const endDate = season === 'fall' ? `${year}-12-20` : season === 'spring' ? `${year}-05-15` : `${year}-08-15`
    try {
      await apiClient.post('/semesters', { name: semName || `${season.charAt(0).toUpperCase() + season.slice(1)} ${year}`, season, year, start_date: startDate, end_date: endDate, is_active: false })
      qc.invalidateQueries({ queryKey: ['semesters'] }); setShowForm(false); setSemName('')
    } catch (ex: unknown) { setErr((ex as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Failed.') }
  }

  return (
    <div>
      <StructureHeader title="Semesters" onAdd={() => setShowForm(!showForm)} />
      {showForm && (
        <div style={s.formCard}>
          <form onSubmit={handleCreate} style={s.inlineForm}>
            <input placeholder="Name (auto-filled if blank)" value={semName} onChange={(e) => setSemName(e.target.value)} style={{ ...s.input, minWidth: '180px' }} />
            <select value={season} onChange={(e) => setSeason(e.target.value)} style={s.input}>
              <option value="fall">Fall</option>
              <option value="spring">Spring</option>
              <option value="summer">Summer</option>
            </select>
            <input type="number" value={year} onChange={(e) => setYear(Number(e.target.value))} style={{ ...s.input, width: '90px' }} required />
            <button type="submit" style={s.primaryBtn}>Add</button>
            {err && <span style={s.errorText}>{err}</span>}
          </form>
        </div>
      )}
      <table style={s.table}>
        <thead><tr><th style={s.th}>Name</th><th style={s.th}>Year</th><th style={s.th}>Season</th><th style={s.th}>Active</th></tr></thead>
        <tbody>
          {semesters?.map((sem) => (
            <tr key={sem.id} style={s.tr}>
              <td style={s.td}>{sem.name}</td>
              <td style={s.td}>{sem.year}</td>
              <td style={s.td}>{sem.season}</td>
              <td style={s.td}>{sem.is_active ? <StatusBadge status="open" /> : <StatusBadge status="closed" />}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function OfferingsTab() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [courseId, setCourseId] = useState(''); const [semId, setSemId] = useState(''); const [instrId, setInstrId] = useState('')
  const [section, setSection] = useState('001'); const [capacity, setCapacity] = useState(30); const [err, setErr] = useState<string | null>(null)

  const { data: offerings } = useQuery<CourseOfferingEnriched[]>({
    queryKey: ['offerings-enriched'],
    queryFn: async () => (await apiClient.get<CourseOfferingEnriched[]>('/admin/course-offerings/enriched')).data,
  })
  const { data: courses } = useQuery<Course[]>({ queryKey: ['courses'], queryFn: async () => (await apiClient.get<Course[]>('/courses')).data })
  const { data: semesters } = useQuery<Semester[]>({ queryKey: ['semesters'], queryFn: async () => (await apiClient.get<Semester[]>('/semesters')).data })
  const { data: users } = useQuery<AdminUser[]>({ queryKey: ['admin-users'], queryFn: async () => (await apiClient.get<AdminUser[]>('/admin/users')).data })
  const instructors = users?.filter((u) => u.role === 'instructor') ?? []

  async function handleCreate(e: FormEvent) {
    e.preventDefault(); setErr(null)
    try {
      await apiClient.post('/course-offerings', { course_id: courseId, semester_id: semId, instructor_id: instrId, section_number: section, capacity })
      qc.invalidateQueries({ queryKey: ['offerings-enriched'] }); setShowForm(false)
    } catch (ex: unknown) { setErr((ex as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Failed.') }
  }

  return (
    <div>
      <StructureHeader title="Course Offerings" onAdd={() => setShowForm(!showForm)} />
      {showForm && (
        <div style={s.formCard}>
          <h4 style={s.formTitle}>New Course Offering</h4>
          <form onSubmit={handleCreate}>
            <div style={s.formGrid}>
              <FormField label="Course">
                <select value={courseId} onChange={(e) => setCourseId(e.target.value)} style={s.input} required>
                  <option value="">— Select course —</option>
                  {courses?.map((c) => <option key={c.id} value={c.id}>{c.code} — {c.name}</option>)}
                </select>
              </FormField>
              <FormField label="Semester">
                <select value={semId} onChange={(e) => setSemId(e.target.value)} style={s.input} required>
                  <option value="">— Select semester —</option>
                  {semesters?.map((sem) => <option key={sem.id} value={sem.id}>{sem.name}</option>)}
                </select>
              </FormField>
              <FormField label="Instructor">
                <select value={instrId} onChange={(e) => setInstrId(e.target.value)} style={s.input} required>
                  <option value="">— Select instructor —</option>
                  {instructors.map((i) => <option key={i.id} value={i.id}>{i.full_name}</option>)}
                </select>
              </FormField>
              <FormField label="Section">
                <input value={section} onChange={(e) => setSection(e.target.value)} style={s.input} required />
              </FormField>
              <FormField label="Capacity">
                <input type="number" min={1} value={capacity} onChange={(e) => setCapacity(Number(e.target.value))} style={s.input} required />
              </FormField>
            </div>
            {err && <p style={s.errorText}>{err}</p>}
            <div style={s.formActions}>
              <button type="submit" style={s.primaryBtn}>Create Offering</button>
            </div>
          </form>
        </div>
      )}
      <table style={s.table}>
        <thead>
          <tr>
            <th style={s.th}>Course</th>
            <th style={s.th}>Semester</th>
            <th style={s.th}>Instructor</th>
            <th style={s.th}>Section</th>
            <th style={s.th}>Enrolled</th>
            <th style={s.th}>Campaign</th>
          </tr>
        </thead>
        <tbody>
          {offerings?.map((o) => (
            <tr key={o.id} style={s.tr}>
              <td style={s.td}><strong>{o.course_code}</strong> {o.course_name}</td>
              <td style={s.td}>{o.semester_name}</td>
              <td style={s.td}>{o.instructor_name}</td>
              <td style={s.td}>{o.section_number}</td>
              <td style={s.td}>{o.enrolled_count} / {o.capacity}</td>
              <td style={s.td}>
                {o.campaign_status ? <StatusBadge status={o.campaign_status} /> : <span style={{ color: '#57606a', fontSize: '0.8rem' }}>None</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ─── Users Section ────────────────────────────────────────────────────────────

function UsersSection() {
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [filter, setFilter] = useState<'all' | 'student' | 'instructor' | 'admin'>('all')
  const [email, setEmail] = useState(''); const [fullName, setFullName] = useState('')
  const [role, setRole] = useState('student'); const [password, setPassword] = useState('')
  const [deptId, setDeptId] = useState(''); const [err, setErr] = useState<string | null>(null)

  const { data: users, isLoading } = useQuery<AdminUser[]>({
    queryKey: ['admin-users'],
    queryFn: async () => (await apiClient.get<AdminUser[]>('/admin/users')).data,
  })
  const { data: depts } = useQuery<Department[]>({ queryKey: ['departments'], queryFn: async () => (await apiClient.get<Department[]>('/departments')).data })

  const filtered = (users ?? []).filter((u) => filter === 'all' || u.role === filter)

  async function handleCreate(e: FormEvent) {
    e.preventDefault(); setErr(null)
    try {
      await apiClient.post('/users', { email, full_name: fullName, role, password, department_id: deptId || null, is_active: true })
      qc.invalidateQueries({ queryKey: ['admin-users'] }); setShowCreate(false)
      setEmail(''); setFullName(''); setPassword(''); setDeptId('')
    } catch (ex: unknown) { setErr((ex as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Failed.') }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <SectionTitle style={{ margin: 0 }}>Users</SectionTitle>
        <button style={s.primaryBtn} onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? 'Cancel' : '+ New User'}
        </button>
      </div>

      {showCreate && (
        <div style={s.formCard}>
          <h4 style={s.formTitle}>Create User</h4>
          <form onSubmit={handleCreate}>
            <div style={s.formGrid}>
              <FormField label="Full Name">
                <input value={fullName} onChange={(e) => setFullName(e.target.value)} style={s.input} required />
              </FormField>
              <FormField label="Email">
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} style={s.input} required />
              </FormField>
              <FormField label="Role">
                <select value={role} onChange={(e) => setRole(e.target.value)} style={s.input}>
                  <option value="student">Student</option>
                  <option value="instructor">Instructor</option>
                  <option value="admin">Admin</option>
                </select>
              </FormField>
              <FormField label="Password">
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={s.input} required minLength={8} />
              </FormField>
              <FormField label="Department (optional)">
                <select value={deptId} onChange={(e) => setDeptId(e.target.value)} style={s.input}>
                  <option value="">— None —</option>
                  {depts?.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                </select>
              </FormField>
            </div>
            {err && <p style={s.errorText}>{err}</p>}
            <div style={s.formActions}>
              <button type="submit" style={s.primaryBtn}>Create User</button>
            </div>
          </form>
        </div>
      )}

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        {(['all', 'student', 'instructor', 'admin'] as const).map((f) => (
          <button key={f} style={filter === f ? s.subTabActive : s.subTab} onClick={() => setFilter(f)}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
            {users && ` (${users.filter((u) => f === 'all' || u.role === f).length})`}
          </button>
        ))}
      </div>

      {isLoading && <p style={s.muted}>Loading…</p>}
      <table style={s.table}>
        <thead>
          <tr>
            <th style={s.th}>Name</th>
            <th style={s.th}>Email</th>
            <th style={s.th}>Role</th>
            <th style={s.th}>Department</th>
            <th style={s.th}>Status</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((u) => (
            <tr key={u.id} style={s.tr}>
              <td style={s.td}>{u.full_name}</td>
              <td style={s.td}>{u.email}</td>
              <td style={s.td}><RoleBadge role={u.role} /></td>
              <td style={s.td}>{u.department_name ?? '—'}</td>
              <td style={s.td}><StatusBadge status={u.is_active ? 'open' : 'closed'} /></td>
            </tr>
          ))}
        </tbody>
      </table>
      {!isLoading && filtered.length === 0 && <EmptyState message="No users found." />}
    </div>
  )
}

// ─── Templates Section ────────────────────────────────────────────────────────

function TemplatesSection() {
  const qc = useQueryClient()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [tName, setTName] = useState(''); const [tDesc, setTDesc] = useState(''); const [tErr, setTErr] = useState<string | null>(null)

  const { data: templates, isLoading } = useQuery<EvalTemplate[]>({
    queryKey: ['templates'],
    queryFn: async () => (await apiClient.get<EvalTemplate[]>('/evaluation-templates')).data,
  })

  async function handleCreateTemplate(e: FormEvent) {
    e.preventDefault(); setTErr(null)
    try {
      const resp = await apiClient.post<EvalTemplate>('/evaluation-templates', { name: tName, description: tDesc, is_active: true })
      qc.invalidateQueries({ queryKey: ['templates'] }); setShowCreate(false); setSelectedId(resp.data.id); setTName(''); setTDesc('')
    } catch (ex: unknown) { setTErr((ex as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Failed.') }
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: '1.5rem', alignItems: 'start' }}>
      {/* Template list */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <strong style={{ fontSize: '0.9rem' }}>Templates</strong>
          <button style={s.primaryBtn} onClick={() => { setShowCreate(!showCreate); setSelectedId(null) }}>+ New</button>
        </div>
        {showCreate && (
          <div style={s.formCard}>
            <form onSubmit={handleCreateTemplate}>
              <input placeholder="Template name" value={tName} onChange={(e) => setTName(e.target.value)} style={{ ...s.input, width: '100%', marginBottom: '0.5rem' }} required />
              <input placeholder="Description (optional)" value={tDesc} onChange={(e) => setTDesc(e.target.value)} style={{ ...s.input, width: '100%', marginBottom: '0.5rem' }} />
              {tErr && <p style={s.errorText}>{tErr}</p>}
              <button type="submit" style={s.primaryBtn}>Create</button>
            </form>
          </div>
        )}
        {isLoading && <p style={s.muted}>Loading…</p>}
        {templates?.map((t) => (
          <div
            key={t.id}
            onClick={() => setSelectedId(t.id)}
            style={{
              padding: '0.75rem 1rem', border: '1px solid #e5e7eb', borderRadius: '6px',
              marginBottom: '0.5rem', cursor: 'pointer', background: selectedId === t.id ? '#eff6ff' : '#fff',
              borderLeft: selectedId === t.id ? '3px solid #3b82d4' : '1px solid #e5e7eb',
            }}
          >
            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{t.name}</div>
            {t.description && <div style={{ fontSize: '0.8rem', color: '#57606a', marginTop: '2px' }}>{t.description}</div>}
          </div>
        ))}
      </div>

      {/* Questions editor */}
      <div>
        {selectedId ? (
          <QuestionsEditor templateId={selectedId} />
        ) : (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#57606a', background: '#f7f8fa', borderRadius: '8px', border: '1px dashed #e5e7eb' }}>
            Select a template to view and edit its questions.
          </div>
        )}
      </div>
    </div>
  )
}

function QuestionsEditor({ templateId }: { templateId: string }) {
  const qc = useQueryClient()
  const [qText, setQText] = useState(''); const [qRequired, setQRequired] = useState(true); const [qErr, setQErr] = useState<string | null>(null)

  const { data: questions } = useQuery<EvalQuestion[]>({
    queryKey: ['template-questions', templateId],
    queryFn: async () => (await apiClient.get<EvalQuestion[]>(`/evaluation-templates/${templateId}/questions`)).data,
  })

  async function handleAddQuestion(e: FormEvent) {
    e.preventDefault(); setQErr(null)
    try {
      await apiClient.post(`/evaluation-templates/${templateId}/questions`, {
        template_id: templateId, text: qText, order_index: (questions?.length ?? 0), is_required: qRequired,
      })
      qc.invalidateQueries({ queryKey: ['template-questions', templateId] }); setQText('')
    } catch (ex: unknown) { setQErr((ex as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Failed.') }
  }

  async function handleDelete(qId: string) {
    if (!window.confirm('Remove this question?')) return
    await apiClient.delete(`/evaluation-templates/${templateId}/questions/${qId}`)
    qc.invalidateQueries({ queryKey: ['template-questions', templateId] })
  }

  return (
    <div>
      <SectionTitle>Questions</SectionTitle>
      {questions && questions.length > 0 ? (
        <table style={s.table}>
          <thead><tr><th style={s.th}>#</th><th style={s.th}>Question Text</th><th style={s.th}>Required</th><th style={s.th}></th></tr></thead>
          <tbody>
            {questions.sort((a, b) => a.order_index - b.order_index).map((q) => (
              <tr key={q.id} style={s.tr}>
                <td style={s.td}>{q.order_index + 1}</td>
                <td style={s.td}>{q.text}</td>
                <td style={s.td}>{q.is_required ? '✓' : '—'}</td>
                <td style={s.td}>
                  <button style={{ ...s.actionBtnRed, padding: '2px 8px' }} onClick={() => handleDelete(q.id)}>Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <EmptyState message="No questions yet. Add the first question below." />
      )}
      <div style={s.formCard}>
        <form onSubmit={handleAddQuestion} style={s.inlineForm}>
          <input
            placeholder="Question text (e.g. How would you rate the overall quality?)"
            value={qText} onChange={(e) => setQText(e.target.value)}
            style={{ ...s.input, flex: 1 }} required
          />
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.875rem', whiteSpace: 'nowrap' }}>
            <input type="checkbox" checked={qRequired} onChange={(e) => setQRequired(e.target.checked)} /> Required
          </label>
          <button type="submit" style={s.primaryBtn}>Add Question</button>
          {qErr && <span style={s.errorText}>{qErr}</span>}
        </form>
      </div>
    </div>
  )
}

// ─── Analytics Section ────────────────────────────────────────────────────────

function AnalyticsSection() {
  const { data: campaigns } = useQuery<CampaignOverview[]>({
    queryKey: ['campaigns-overview'],
    queryFn: async () => (await apiClient.get<CampaignOverview[]>('/admin/campaigns/overview')).data,
  })
  const { data: kpis, error: kpisError } = useQuery<DashboardKPI>({
    queryKey: ['dashboard-kpis'],
    queryFn: async () => (await apiClient.get<DashboardKPI>('/analytics/dashboard')).data,
    retry: false,
  })

  const closedWithStats = campaigns?.filter((c) => c.status === 'closed') ?? []
  const openCampaigns = campaigns?.filter((c) => c.status === 'open') ?? []

  return (
    <div>
      {kpisError && (
        <InfoBox type="warning">
          Analytics service is unavailable. Statistics cannot be computed. The Java analytics service may be starting up.
        </InfoBox>
      )}

      {kpis && (
        <>
          <SectionTitle>University-Wide KPIs</SectionTitle>
          <div style={s.kpiGrid}>
            <KPICard label="Total Campaigns" value={kpis.totalCampaigns} color="#3b82d4" />
            <KPICard label="Active Campaigns" value={kpis.activeCampaigns} color="#16a34a" />
            <KPICard label="Total Submissions" value={kpis.totalSubmissions} color="#7c3aed" />
            <KPICard label="Avg Rating" value={kpis.averageRating > 0 ? kpis.averageRating.toFixed(2) : '—'} color="#d97706" />
            <KPICard label="Response Rate" value={`${kpis.overallResponseRate ?? 0}%`} color="#0891b2" />
          </div>
        </>
      )}

      {openCampaigns.length > 0 && (
        <>
          <SectionTitle>Open Campaigns — Live Progress</SectionTitle>
          <table style={s.table}>
            <thead><tr>
              <th style={s.th}>Course</th><th style={s.th}>Semester</th>
              <th style={s.th}>Submissions</th><th style={s.th}>Rate</th>
            </tr></thead>
            <tbody>
              {openCampaigns.map((c) => {
                const rate = c.enrolled_count > 0 ? Math.round(c.submission_count / c.enrolled_count * 100) : 0
                return (
                  <tr key={c.id} style={s.tr}>
                    <td style={s.td}><strong>{c.course_code}</strong> {c.course_name}</td>
                    <td style={s.td}>{c.semester_name}</td>
                    <td style={s.td}>{c.submission_count} / {c.enrolled_count}</td>
                    <td style={s.td}><ProgressBar value={rate} /></td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </>
      )}

      {closedWithStats.length > 0 && (
        <>
          <SectionTitle>Closed Campaign Results</SectionTitle>
          {closedWithStats.map((c) => (
            <CampaignStatsCard key={c.id} campaign={c} />
          ))}
        </>
      )}

      {(!kpis || (closedWithStats.length === 0 && openCampaigns.length === 0)) && !kpisError && (
        <EmptyState message="No evaluation data yet. Create and run campaigns to see analytics." />
      )}
    </div>
  )
}

function CampaignStatsCard({ campaign }: { campaign: CampaignOverview }) {
  const [expanded, setExpanded] = useState(false)

  const { data: stats, isLoading, error } = useQuery<Record<string, unknown>>({
    queryKey: ['campaign-stats', campaign.id],
    queryFn: async () => (await apiClient.get(`/analytics/campaigns/${campaign.id}/stats`)).data,
    enabled: expanded,
    retry: false,
  })

  const questionStats = (stats?.questionStats as Array<{
    questionId: string; questionText: string; average: number
    distribution: Record<string, number>
  }>) ?? []

  return (
    <div style={{ ...s.card, marginBottom: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <strong>{campaign.course_code} — {campaign.course_name}</strong>
          <span style={{ marginLeft: '0.75rem', color: '#57606a', fontSize: '0.875rem' }}>{campaign.semester_name} · {campaign.instructor_name}</span>
        </div>
        <button style={s.subTab} onClick={() => setExpanded(!expanded)}>
          {expanded ? 'Hide Results' : 'View Results'}
        </button>
      </div>
      {expanded && (
        <div style={{ marginTop: '1rem' }}>
          {isLoading && <p style={s.muted}>Loading…</p>}
          {error && <p style={s.errorText}>Analytics unavailable.</p>}
          {stats && !('threshold' in stats) && (
            <>
              <div style={s.kpiGrid}>
                <KPICard label="Overall Avg" value={(stats.overallAverage as number)?.toFixed(2)} />
                <KPICard label="Submissions" value={stats.totalSubmissions as number} />
                <KPICard label="Enrolled" value={stats.totalEnrolled as number} />
                <KPICard label="Response Rate" value={`${stats.responseRate as number}%`} />
              </div>
              {questionStats.length > 0 && (
                <table style={s.table}>
                  <thead>
                    <tr>
                      <th style={s.th}>Question</th>
                      <th style={s.th}>Avg</th>
                      <th style={s.th}>1</th><th style={s.th}>2</th><th style={s.th}>3</th><th style={s.th}>4</th><th style={s.th}>5</th>
                    </tr>
                  </thead>
                  <tbody>
                    {questionStats.map((qs) => (
                      <tr key={qs.questionId} style={s.tr}>
                        <td style={s.td}>{qs.questionText}</td>
                        <td style={{ ...s.td, fontWeight: 700 }}>{qs.average.toFixed(2)}</td>
                        {[1,2,3,4,5].map((r) => <td key={r} style={s.td}>{qs.distribution[r] ?? 0}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
              <AIInsightsPanel campaignId={campaign.id} />
            </>
          )}
          {stats && 'threshold' in stats && (
            <InfoBox type="info">
              Results hidden — minimum {campaign.min_responses_threshold} responses required.
              Currently: {stats.totalSubmissions as number}.
            </InfoBox>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Reports Section ──────────────────────────────────────────────────────────

function ReportsSection() {
  const [downloading, setDownloading] = useState<string | null>(null)
  const [dlError, setDlError] = useState<string | null>(null)

  const { data: campaigns } = useQuery<CampaignOverview[]>({
    queryKey: ['campaigns-overview'],
    queryFn: async () => (await apiClient.get<CampaignOverview[]>('/admin/campaigns/overview')).data,
  })

  const closedCampaigns = campaigns?.filter((c) => c.status === 'closed') ?? []

  async function downloadCSV(campaignId: string, courseName: string) {
    setDownloading(campaignId); setDlError(null)
    try {
      const resp = await apiClient.get(`/analytics/campaigns/${campaignId}/export-csv`, {
        responseType: 'blob',
      })
      const url = URL.createObjectURL(new Blob([resp.data as BlobPart], { type: 'text/csv' }))
      const a = document.createElement('a')
      a.href = url; a.download = `evaluation-${courseName.replace(/\s+/g, '-')}-${campaignId.slice(0, 8)}.csv`
      document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url)
    } catch {
      setDlError('Export failed. Please try again.')
    } finally {
      setDownloading(null)
    }
  }

  return (
    <div>
      <SectionTitle>Export Reports</SectionTitle>
      <p style={s.muted}>
        Export campaign evaluation data as CSV. Reports contain aggregated statistics only —
        no individual student identities are included.
      </p>

      {dlError && <InfoBox type="error">{dlError}</InfoBox>}

      {closedCampaigns.length === 0 && (
        <EmptyState message="No closed campaigns available for export. Close a campaign to enable CSV export." />
      )}

      {closedCampaigns.length > 0 && (
        <table style={s.table}>
          <thead>
            <tr>
              <th style={s.th}>Course</th>
              <th style={s.th}>Semester</th>
              <th style={s.th}>Submissions</th>
              <th style={s.th}>Export</th>
            </tr>
          </thead>
          <tbody>
            {closedCampaigns.map((c) => (
              <tr key={c.id} style={s.tr}>
                <td style={s.td}><strong>{c.course_code}</strong> {c.course_name}</td>
                <td style={s.td}>{c.semester_name}</td>
                <td style={s.td}>{c.submission_count}</td>
                <td style={s.td}>
                  <button
                    style={s.primaryBtn}
                    disabled={downloading === c.id}
                    onClick={() => downloadCSV(c.id, c.course_name)}
                  >
                    {downloading === c.id ? 'Exporting…' : '↓ CSV'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

// ─── Shared sub-components ────────────────────────────────────────────────────

function KPICard({ label, value, color = '#57606a' }: { label: string; value: number | string; color?: string }) {
  return (
    <div style={s.kpiCard}>
      <div style={{ fontSize: '1.6rem', fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: '0.78rem', color: '#57606a', marginTop: '0.2rem' }}>{label}</div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { bg: string; text: string; label: string }> = {
    open:   { bg: '#d1fae5', text: '#065f46', label: 'Open' },
    closed: { bg: '#f3f4f6', text: '#6b7280', label: 'Closed' },
    draft:  { bg: '#fef3c7', text: '#92400e', label: 'Draft' },
  }
  const c = map[status] ?? { bg: '#f3f4f6', text: '#6b7280', label: status }
  return <span style={{ display: 'inline-block', padding: '2px 10px', borderRadius: '12px', fontSize: '0.78rem', fontWeight: 600, background: c.bg, color: c.text }}>{c.label}</span>
}

function RoleBadge({ role }: { role: string }) {
  const map: Record<string, { bg: string; text: string }> = {
    admin:      { bg: '#fee2e2', text: '#991b1b' },
    instructor: { bg: '#e0f2fe', text: '#0369a1' },
    student:    { bg: '#f0fdf4', text: '#166534' },
  }
  const c = map[role] ?? { bg: '#f3f4f6', text: '#6b7280' }
  return <span style={{ display: 'inline-block', padding: '2px 10px', borderRadius: '12px', fontSize: '0.78rem', fontWeight: 600, background: c.bg, color: c.text }}>{role}</span>
}

function ProgressBar({ value }: { value: number }) {
  const pct = Math.min(100, Math.max(0, value))
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <div style={{ flex: 1, height: '6px', background: '#e5e7eb', borderRadius: '3px', overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: pct >= 80 ? '#16a34a' : pct >= 50 ? '#d97706' : '#dc2626', borderRadius: '3px' }} />
      </div>
      <span style={{ fontSize: '0.8rem', color: '#57606a', minWidth: '36px' }}>{pct}%</span>
    </div>
  )
}

function SectionTitle({ children, style: extraStyle }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return <h2 style={{ margin: '0 0 1rem', fontSize: '1rem', fontWeight: 600, color: '#1f2328', ...extraStyle }}>{children}</h2>
}

function StructureHeader({ title, onAdd }: { title: string; onAdd: () => void }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
      <SectionTitle style={{ margin: 0 }}>{title}</SectionTitle>
      <button style={s.primaryBtn} onClick={onAdd}>+ Add</button>
    </div>
  )
}

function FormField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#57606a', marginBottom: '0.25rem' }}>{label}</label>
      {children}
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div style={{ padding: '2rem', textAlign: 'center', color: '#57606a', background: '#f7f8fa', border: '1px dashed #e5e7eb', borderRadius: '8px', fontSize: '0.9rem' }}>
      {message}
    </div>
  )
}

function InfoBox({ type, children }: { type: 'info' | 'warning' | 'error'; children: React.ReactNode }) {
  const colors = {
    info:    { bg: '#eff6ff', border: '#3b82f6', text: '#1e40af' },
    warning: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
    error:   { bg: '#fee2e2', border: '#dc2626', text: '#991b1b' },
  }
  const c = colors[type]
  return (
    <div style={{ background: c.bg, border: `1px solid ${c.border}`, borderRadius: '6px', padding: '0.75rem 1rem', fontSize: '0.875rem', color: c.text, marginBottom: '1rem' }}>
      {children}
    </div>
  )
}

// ─── Shared styles ────────────────────────────────────────────────────────────

const s: Record<string, React.CSSProperties> = {
  card: { background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1.25rem' },
  kpiGrid: { display: 'flex', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1.5rem' },
  kpiCard: { background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem 1.25rem', minWidth: '110px', textAlign: 'center' },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden', marginBottom: '1.5rem', fontSize: '0.875rem' },
  th: { padding: '0.6rem 1rem', textAlign: 'left', background: '#f7f8fa', fontSize: '0.78rem', fontWeight: 600, color: '#57606a', borderBottom: '1px solid #e5e7eb' },
  tr: { borderBottom: '1px solid #f3f4f6' },
  td: { padding: '0.65rem 1rem', color: '#1f2328' },
  muted: { color: '#57606a', fontSize: '0.875rem', margin: '0 0 1rem' },
  errorText: { color: '#c0392b', fontSize: '0.8rem', margin: '0.25rem 0' },
  helpText: { display: 'block', fontSize: '0.78rem', color: '#57606a', marginTop: '0.25rem' },
  primaryBtn: { padding: '0.4rem 1rem', background: '#3b82d4', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 },
  actionBtnGreen: { padding: '0.3rem 0.75rem', background: '#16a34a', color: '#fff', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '0.78rem', fontWeight: 600, marginRight: '4px' },
  actionBtnRed: { padding: '0.3rem 0.75rem', background: '#dc2626', color: '#fff', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '0.78rem', fontWeight: 600 },
  closedLabel: { fontSize: '0.78rem', color: '#57606a', fontStyle: 'italic' },
  input: { padding: '0.4rem 0.6rem', border: '1px solid #e5e7eb', borderRadius: '5px', fontSize: '0.875rem', outline: 'none', minWidth: '120px' },
  formCard: { background: '#f7f8fa', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' },
  formTitle: { margin: '0 0 0.75rem', fontSize: '0.9rem', fontWeight: 600 },
  formGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.75rem', marginBottom: '0.75rem' },
  formActions: { display: 'flex', justifyContent: 'flex-end', marginTop: '0.75rem' },
  inlineForm: { display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' },
  subTab: { padding: '0.35rem 0.9rem', background: 'transparent', border: '1px solid #e5e7eb', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem', color: '#57606a' },
  subTabActive: { padding: '0.35rem 0.9rem', background: '#3b82d4', border: '1px solid #3b82d4', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem', color: '#fff', fontWeight: 600 },
}


