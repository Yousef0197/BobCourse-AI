/**
 * Evaluation submission form — student submits ratings + optional comment.
 */
import { useState, FormEvent } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from '../lib/apiClient'

interface Question {
  id: string
  text: string
  order_index: number
  is_required: boolean
}

export default function SubmissionForm() {
  const { campaignId } = useParams<{ campaignId: string }>()
  const navigate = useNavigate()
const queryClient = useQueryClient()
  const [ratings, setRatings] = useState<Record<string, number>>({})
  const [comment, setComment] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const { data: questions, isLoading, error } = useQuery<Question[]>({
    queryKey: ['campaign-questions', campaignId],
    queryFn: async () => {
      const resp = await apiClient.get<Question[]>(`/evaluation-campaigns/${campaignId}/questions`)
      return resp.data
    },
    enabled: !!campaignId,
  })

  function setRating(questionId: string, rating: number) {
    setRatings((prev) => ({ ...prev, [questionId]: rating }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!questions) return
    // Validate all required questions have a rating
    for (const q of questions) {
      if (q.is_required && !ratings[q.id]) {
        setSubmitError(`Please rate: "${q.text}"`)
        return
      }
    }
    setSubmitError(null)
    setSubmitting(true)
    try {
      await apiClient.post('/submissions', {
        campaign_id: campaignId,
        answers: Object.entries(ratings).map(([question_id, rating]) => ({ question_id, rating })),
        comment: comment.trim() || undefined,
      })
      await queryClient.invalidateQueries({ queryKey: ['my-enrollments'] })
    navigate('/student', { state: { submitted: true } })
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status: number; data?: { detail?: string } } }
      if (axiosErr.response?.status === 409) {
        setSubmitError('You have already submitted an evaluation for this course.')
      } else if (axiosErr.response?.status === 403) {
        setSubmitError(axiosErr.response.data?.detail ?? 'Submission not allowed.')
      } else {
        setSubmitError('Submission failed. Please try again.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  if (isLoading) return <div style={styles.page}><p style={styles.muted}>Loading questions…</p></div>
  if (error) return <div style={styles.page}><p style={styles.errorText}>Failed to load evaluation questions.</p></div>

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.h1}>Course Evaluation</h1>
        <p style={styles.subtitle}>Rate each question from 1 (poor) to 5 (excellent).</p>

        <form onSubmit={handleSubmit}>
          {questions?.map((q) => (
            <div key={q.id} style={styles.questionBlock}>
              <p style={styles.questionText}>
                {q.order_index + 1}. {q.text}
                {q.is_required && <span style={styles.required}> *</span>}
              </p>
              <div style={styles.ratingRow}>
                {[1, 2, 3, 4, 5].map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => setRating(q.id, r)}
                    style={ratings[q.id] === r ? styles.ratingBtnActive : styles.ratingBtn}
                  >
                    {r}
                  </button>
                ))}
                <span style={styles.ratingLabel}>
                  {ratings[q.id] ? ['', 'Poor', 'Below average', 'Average', 'Good', 'Excellent'][ratings[q.id]] : ''}
                </span>
              </div>
            </div>
          ))}

          <div style={styles.questionBlock}>
            <p style={styles.questionText}>Additional comments (optional)</p>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              maxLength={2000}
              rows={4}
              style={styles.textarea}
              placeholder="Share any additional feedback (max 2000 characters)…"
            />
            <p style={styles.charCount}>{comment.length}/2000</p>
          </div>

          {submitError && <p style={styles.errorText}>{submitError}</p>}

          <div style={styles.actions}>
            <button type="button" onClick={() => navigate('/student')} style={styles.cancelBtn}>
              Cancel
            </button>
            <button type="submit" disabled={submitting} style={styles.submitBtn}>
              {submitting ? 'Submitting…' : 'Submit Evaluation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  page: { fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif', minHeight: '100vh', background: '#f7f8fa', padding: '2rem 1rem' },
  card: { maxWidth: '700px', margin: '0 auto', background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '2rem' },
  h1: { margin: '0 0 0.5rem', fontSize: '1.4rem', color: '#1f2328' },
  subtitle: { margin: '0 0 1.5rem', fontSize: '0.9rem', color: '#57606a' },
  questionBlock: { marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid #e5e7eb' },
  questionText: { margin: '0 0 0.75rem', fontWeight: 600, color: '#1f2328' },
  required: { color: '#c0392b' },
  ratingRow: { display: 'flex', gap: '0.5rem', alignItems: 'center' },
  ratingBtn: { width: '40px', height: '40px', border: '1px solid #e5e7eb', borderRadius: '6px', background: '#f7f8fa', cursor: 'pointer', fontSize: '1rem', fontWeight: 600, color: '#57606a' },
  ratingBtnActive: { width: '40px', height: '40px', border: '2px solid #3b82d4', borderRadius: '6px', background: '#dbeafe', cursor: 'pointer', fontSize: '1rem', fontWeight: 700, color: '#1e40af' },
  ratingLabel: { marginLeft: '0.5rem', fontSize: '0.85rem', color: '#57606a', fontStyle: 'italic' },
  textarea: { width: '100%', padding: '0.75rem', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '0.9rem', resize: 'vertical', boxSizing: 'border-box' },
  charCount: { margin: '0.25rem 0 0', textAlign: 'right', fontSize: '0.8rem', color: '#57606a' },
  errorText: { color: '#c0392b', fontSize: '0.875rem', margin: '0 0 1rem' },
  muted: { color: '#57606a', fontSize: '0.9rem' },
  actions: { display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '0.5rem' },
  cancelBtn: { padding: '0.5rem 1.25rem', background: 'transparent', border: '1px solid #e5e7eb', borderRadius: '6px', cursor: 'pointer', fontSize: '0.9rem' },
  submitBtn: { padding: '0.5rem 1.5rem', background: '#3b82d4', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.9rem', fontWeight: 600 },
}


