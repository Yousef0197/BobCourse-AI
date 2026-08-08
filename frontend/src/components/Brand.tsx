type BrandProps = {
  compact?: boolean
  subtitle?: string
}

export default function Brand({
  compact = false,
  subtitle = 'Course Evaluation Intelligence',
}: BrandProps) {
  return (
    <div className={`bc-brand${compact ? ' bc-brand--compact' : ''}`} aria-label="BobCourse AI">
      <div className="bc-brand__mark" aria-hidden="true">
        <span className="bc-brand__letter">B</span>
        <span className="bc-brand__spark">✦</span>
      </div>

      <div className="bc-brand__copy">
        <div className="bc-brand__name">
          BobCourse <span>AI</span>
        </div>

        {!compact && (
          <div className="bc-brand__subtitle">
            {subtitle}
          </div>
        )}
      </div>
    </div>
  )
}
