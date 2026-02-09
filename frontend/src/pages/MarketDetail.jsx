import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { fetchAPI } from '../api'
import { useAuth } from '../context/AuthContext'
import TradingPanel from '../components/TradingPanel'

export default function MarketDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const [market, setMarket] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [resolving, setResolving] = useState(false)

  const loadMarket = async () => {
    try {
      const [mkt, txns] = await Promise.all([
        fetchAPI(`/markets/${id}`),
        fetchAPI(`/markets/${id}/transactions`),
      ])
      setMarket(mkt)
      setTransactions(txns)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMarket()
  }, [id])

  const handleTradeComplete = (result) => {
    setMarket(prev => ({
      ...prev,
      price_yes: result.price_yes,
      price_no: result.price_no,
    }))
    loadMarket()
  }

  const handleResolve = async (outcome) => {
    if (!window.confirm(`Are you sure you want to resolve this market as ${outcome ? 'YES' : 'NO'}?`)) {
      return
    }
    setResolving(true)
    try {
      await fetchAPI(`/markets/${id}/resolve`, {
        method: 'POST',
        body: JSON.stringify({ outcome }),
      })
      loadMarket()
    } catch (err) {
      alert(err.message)
    } finally {
      setResolving(false)
    }
  }

  if (loading) {
    return <p style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading...</p>
  }

  if (!market) {
    return <p style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Market not found</p>
  }

  const resDate = new Date(market.resolution_date).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric'
  })
  const createdDate = new Date(market.created_at).toLocaleDateString()

  return (
    <div className="market-detail">
      <div className="market-info">
        <div className="card">
          <div style={{ marginBottom: '0.5rem' }}>
            {market.resolved ? (
              <span className={`badge ${market.outcome ? 'badge-yes' : 'badge-no'}`} style={{ fontSize: '0.85rem' }}>
                Resolved {market.outcome ? 'YES' : 'NO'}
              </span>
            ) : (
              <span className="badge badge-active">Active</span>
            )}
          </div>

          <h1>{market.title}</h1>

          {market.description && (
            <p className="market-description">{market.description}</p>
          )}

          <div className="market-meta-grid">
            <div className="meta-item">
              <div className="meta-label">Yes Price</div>
              <div className="meta-value" style={{ color: 'var(--green)' }}>
                {(market.price_yes * 100).toFixed(1)}%
              </div>
            </div>
            <div className="meta-item">
              <div className="meta-label">No Price</div>
              <div className="meta-value" style={{ color: 'var(--red)' }}>
                {(market.price_no * 100).toFixed(1)}%
              </div>
            </div>
            <div className="meta-item">
              <div className="meta-label">Resolution Date</div>
              <div className="meta-value">{resDate}</div>
            </div>
            <div className="meta-item">
              <div className="meta-label">Volume</div>
              <div className="meta-value">${(market.total_volume || 0).toFixed(0)}</div>
            </div>
          </div>

          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Created by <strong>{market.creator_username}</strong> on {createdDate}
          </div>

          {/* Resolve panel for creator */}
          {user && user.id === market.creator_id && !market.resolved && (
            <div className="resolve-panel">
              <h4>Resolve this market</h4>
              <div className="resolve-buttons">
                <button
                  className="btn btn-green"
                  onClick={() => handleResolve(true)}
                  disabled={resolving}
                >
                  Resolve YES
                </button>
                <button
                  className="btn btn-red"
                  onClick={() => handleResolve(false)}
                  disabled={resolving}
                >
                  Resolve NO
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Transaction history */}
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Recent Trades</h3>
          {transactions.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '1rem' }}>
              No trades yet. Be the first!
            </p>
          ) : (
            <table className="transactions-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Action</th>
                  <th>Shares</th>
                  <th>Price</th>
                  <th>Cost</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(txn => (
                  <tr key={txn.id}>
                    <td>{txn.username}</td>
                    <td>
                      <span className={txn.action === 'buy' ? 'badge-yes' : 'badge-no'}>
                        {txn.action.toUpperCase()}
                      </span>
                      {' '}
                      <span className={txn.outcome === 'yes' ? 'badge-yes' : 'badge-no'}>
                        {txn.outcome.toUpperCase()}
                      </span>
                    </td>
                    <td>{txn.shares.toFixed(1)}</td>
                    <td>${txn.price_per_share.toFixed(4)}</td>
                    <td>${Math.abs(txn.total_cost).toFixed(2)}</td>
                    <td>{new Date(txn.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <TradingPanel market={market} onTradeComplete={handleTradeComplete} />
    </div>
  )
}
