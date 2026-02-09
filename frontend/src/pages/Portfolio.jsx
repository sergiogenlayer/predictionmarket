import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchAPI } from '../api'
import { useAuth } from '../context/AuthContext'

export default function Portfolio() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [positions, setPositions] = useState([])
  const [leaderboard, setLeaderboard] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }
    loadData()
  }, [user])

  const loadData = async () => {
    try {
      const [pos, lb] = await Promise.all([
        fetchAPI('/users/me/positions'),
        fetchAPI('/users/leaderboard'),
      ])
      setPositions(pos)
      setLeaderboard(lb)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (!user) return null

  if (loading) {
    return <p style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading...</p>
  }

  const totalValue = positions.reduce((sum, p) => {
    return sum + p.shares_yes * p.current_price_yes + p.shares_no * p.current_price_no
  }, 0)

  return (
    <div>
      <h1 className="page-title" style={{ marginBottom: '1.5rem' }}>Portfolio</h1>

      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.3rem' }}>Cash Balance</div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--green)' }}>
            ${user.balance.toFixed(2)}
          </div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.3rem' }}>Position Value</div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--accent)' }}>
            ${totalValue.toFixed(2)}
          </div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.3rem' }}>Total Value</div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>
            ${(user.balance + totalValue).toFixed(2)}
          </div>
        </div>
      </div>

      {/* Positions */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>Your Positions</h3>
        {positions.length === 0 ? (
          <div className="empty-state">
            <p>No positions yet</p>
            <Link to="/" className="btn btn-primary">Browse markets</Link>
          </div>
        ) : (
          <div className="positions-grid">
            {positions.map(pos => (
              <Link
                key={pos.market_id}
                to={`/market/${pos.market_id}`}
                style={{ textDecoration: 'none', color: 'inherit' }}
              >
                <div className="card position-card">
                  <div>
                    <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>{pos.market_title}</div>
                    {pos.market_resolved && (
                      <span className={`badge ${pos.market_outcome ? 'badge-yes' : 'badge-no'}`}>
                        Resolved {pos.market_outcome ? 'YES' : 'NO'}
                      </span>
                    )}
                  </div>
                  <div className="position-shares">
                    {pos.shares_yes > 0 && (
                      <div className="position-share-item">
                        <div className="position-share-label">Yes</div>
                        <div className="position-share-value" style={{ color: 'var(--green)' }}>
                          {pos.shares_yes.toFixed(1)}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          ${(pos.shares_yes * pos.current_price_yes).toFixed(2)}
                        </div>
                      </div>
                    )}
                    {pos.shares_no > 0 && (
                      <div className="position-share-item">
                        <div className="position-share-label">No</div>
                        <div className="position-share-value" style={{ color: 'var(--red)' }}>
                          {pos.shares_no.toFixed(1)}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          ${(pos.shares_no * pos.current_price_no).toFixed(2)}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Leaderboard */}
      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Leaderboard</h3>
        {leaderboard.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No users yet</p>
        ) : (
          <ul className="leaderboard-list">
            {leaderboard.map(entry => (
              <li key={entry.username} className="leaderboard-item">
                <span className="leaderboard-rank">#{entry.rank}</span>
                <span className="leaderboard-name">
                  {entry.username}
                  {entry.username === user.username && ' (you)'}
                </span>
                <span className="leaderboard-balance">${entry.balance.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
