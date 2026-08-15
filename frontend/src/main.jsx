import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

function ScoreBar({ value }) {
  const percent = Math.round((value || 0) * 100)
  return (
    <div className="score-wrap">
      <div className="score-track"><div className="score-fill" style={{ width: `${percent}%` }} /></div>
      <span>{percent}%</span>
    </div>
  )
}

function App() {
  const [runs, setRuns] = useState([])
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')

  const loadRuns = async () => {
    try {
      const response = await fetch(`${API}/runs`)
      if (!response.ok) throw new Error('Could not load evaluation runs')
      const data = await response.json()
      setRuns(data)
      if (!selected && data.length) setSelected(data[0])
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => { loadRuns() }, [])

  return (
    <main>
      <header>
        <p className="eyebrow">AI EVALUATION</p>
        <h1>Benchmark Review</h1>
        <p className="subtitle">Compare model quality, latency, and failure cases across evaluation runs.</p>
      </header>

      {error && <div className="notice">{error}. Start the backend and create a sample run to populate the dashboard.</div>}

      <section className="layout">
        <aside>
          <div className="panel-title">Recent runs</div>
          {runs.length === 0 && <p className="muted">No runs yet.</p>}
          {runs.map(run => (
            <button className={`run ${selected?.id === run.id ? 'active' : ''}`} key={run.id} onClick={() => setSelected(run)}>
              <strong>{run.model_name}</strong>
              <span>{run.suite_name}</span>
              <small>{Math.round(run.average_score * 100)}% avg score</small>
            </button>
          ))}
        </aside>

        <section className="content">
          {!selected ? <div className="empty">Select an evaluation run to inspect results.</div> : <>
            <div className="metrics">
              <article><span>Average score</span><strong>{Math.round(selected.average_score * 100)}%</strong></article>
              <article><span>Pass rate</span><strong>{Math.round(selected.pass_rate * 100)}%</strong></article>
              <article><span>Avg latency</span><strong>{selected.average_latency_ms ? `${selected.average_latency_ms} ms` : '—'}</strong></article>
            </div>
            <div className="table-card">
              <div className="panel-title">Test cases</div>
              <table>
                <thead><tr><th>Case</th><th>Category</th><th>Score</th><th>Status</th></tr></thead>
                <tbody>
                  {selected.scores?.map(score => (
                    <tr key={score.case_id}>
                      <td>{score.case_id}</td>
                      <td>{score.category}</td>
                      <td><ScoreBar value={score.final_score} /></td>
                      <td><span className={`pill ${score.passed ? 'pass' : 'fail'}`}>{score.passed ? 'Pass' : 'Review'}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>}
        </section>
      </section>
    </main>
  )
}

createRoot(document.getElementById('root')).render(<App />)
