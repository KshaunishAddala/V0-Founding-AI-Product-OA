import { useState } from 'react'

interface Props {
  onRefresh: () => void
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function SummarySection({ onRefresh }: Props) {
  const [tags, setTags] = useState('')
  const [summary, setSummary] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const generateSummary = async () => {
    setLoading(true)
    setError('')
    
    try {
      const tagList = tags
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0)

      const res = await fetch(`${API_URL}/api/summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tags: tagList })
      })

      if (!res.ok) throw new Error('Failed to generate summary')

      const data = await res.json()
      setSummary(data.summary)
      onRefresh()
    } catch (err) {
      setError('Could not generate summary. Check your connection and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="summary-section">
      <div className="summary-controls">
        <input
          type="text"
          value={tags}
          onChange={e => setTags(e.target.value)}
          placeholder="Enter topics (e.g., AI, startups, crypto)"
          className="tag-input"
        />
        <button 
          onClick={generateSummary} 
          disabled={loading}
          className="generate-btn"
        >
          {loading ? 'Generating...' : 'Get Summary'}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {summary && (
        <div className="summary-content">
          <h2>Today's Tech Roundup</h2>
          <div className="summary-text">
            {summary.split('\n').map((p, i) => p && <p key={i}>{p}</p>)}
          </div>
        </div>
      )}
    </section>
  )
}
