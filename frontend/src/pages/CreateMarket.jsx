import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchAPI } from '../api'
import { useAuth } from '../context/AuthContext'

export default function CreateMarket() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [resolutionDate, setResolutionDate] = useState('')
  const [liquidity, setLiquidity] = useState(100)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (!user) {
    navigate('/login')
    return null
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const market = await fetchAPI('/markets', {
        method: 'POST',
        body: JSON.stringify({
          title,
          description,
          resolution_date: new Date(resolutionDate).toISOString(),
          liquidity_param: liquidity,
        }),
      })
      navigate(`/market/${market.id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Default date: 1 month from now
  const defaultDate = new Date()
  defaultDate.setMonth(defaultDate.getMonth() + 1)
  const minDate = new Date().toISOString().split('T')[0]

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h1 className="page-title" style={{ marginBottom: '1.5rem' }}>Create New Market</h1>

      <div className="card" style={{ padding: '2rem' }}>
        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Question</label>
            <input
              type="text"
              placeholder="Will X happen by Y?"
              value={title}
              onChange={e => setTitle(e.target.value)}
              required
              minLength={10}
              maxLength={200}
            />
          </div>

          <div className="form-group">
            <label>Description (optional)</label>
            <textarea
              placeholder="Provide context and resolution criteria..."
              value={description}
              onChange={e => setDescription(e.target.value)}
              maxLength={2000}
            />
          </div>

          <div className="form-group">
            <label>Resolution Date</label>
            <input
              type="date"
              value={resolutionDate}
              onChange={e => setResolutionDate(e.target.value)}
              min={minDate}
              required
            />
          </div>

          <div className="form-group">
            <label>
              Liquidity Parameter (b = {liquidity})
            </label>
            <input
              type="range"
              min="10"
              max="500"
              step="10"
              value={liquidity}
              onChange={e => setLiquidity(Number(e.target.value))}
            />
            <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              Higher = more liquidity, smaller price impact per trade. Default: 100
            </small>
          </div>

          <button
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.8rem', fontSize: '1rem' }}
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Market'}
          </button>
        </form>
      </div>
    </div>
  )
}
