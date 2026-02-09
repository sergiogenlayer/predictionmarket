import { useState } from 'react'
import { fetchAPI } from '../api'
import { useAuth } from '../context/AuthContext'

// Client-side LMSR for cost preview
function lmsrCostFunction(qYes, qNo, b) {
  const maxQ = Math.max(qYes, qNo) / b
  return b * (maxQ + Math.log(
    Math.exp(qYes / b - maxQ) + Math.exp(qNo / b - maxQ)
  ))
}

function calculateCost(qYes, qNo, b, outcome, shares, action) {
  let newCost, oldCost
  oldCost = lmsrCostFunction(qYes, qNo, b)

  if (action === 'buy') {
    if (outcome === 'yes') {
      newCost = lmsrCostFunction(qYes + shares, qNo, b)
    } else {
      newCost = lmsrCostFunction(qYes, qNo + shares, b)
    }
    return newCost - oldCost
  } else {
    if (outcome === 'yes') {
      newCost = lmsrCostFunction(qYes - shares, qNo, b)
    } else {
      newCost = lmsrCostFunction(qYes, qNo - shares, b)
    }
    return oldCost - newCost // proceeds
  }
}

export default function TradingPanel({ market, onTradeComplete }) {
  const { user, refreshUser } = useAuth()
  const [action, setAction] = useState('buy')
  const [outcome, setOutcome] = useState('yes')
  const [shares, setShares] = useState(10)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  if (!user) {
    return (
      <div className="card trading-panel">
        <h3>Trade</h3>
        <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem 0' }}>
          Please <a href="/login">log in</a> to trade
        </p>
      </div>
    )
  }

  if (market.resolved) {
    return (
      <div className="card trading-panel">
        <h3>Market Resolved</h3>
        <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem 0' }}>
          Outcome: <strong className={market.outcome ? 'badge-yes' : 'badge-no'}>
            {market.outcome ? 'YES' : 'NO'}
          </strong>
        </p>
      </div>
    )
  }

  const cost = shares > 0
    ? calculateCost(market.q_yes, market.q_no, market.liquidity_param, outcome, shares, action)
    : 0
  const avgPrice = shares > 0 ? cost / shares : 0

  const handleTrade = async () => {
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const result = await fetchAPI(`/markets/${market.id}/trade`, {
        method: 'POST',
        body: JSON.stringify({ outcome, action, shares }),
      })
      setSuccess(result.message)
      await refreshUser()
      if (onTradeComplete) onTradeComplete(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card trading-panel">
      <h3>Trade</h3>

      <div className="trade-tabs">
        <button
          className={`trade-tab ${action === 'buy' ? 'active-buy' : ''}`}
          onClick={() => { setAction('buy'); setError(''); setSuccess('') }}
        >
          Buy
        </button>
        <button
          className={`trade-tab ${action === 'sell' ? 'active-sell' : ''}`}
          onClick={() => { setAction('sell'); setError(''); setSuccess('') }}
        >
          Sell
        </button>
      </div>

      <div className="outcome-selector">
        <button
          className={`outcome-btn ${outcome === 'yes' ? 'selected-yes' : ''}`}
          onClick={() => setOutcome('yes')}
        >
          <div className="outcome-btn-label">Yes</div>
          <div className="outcome-btn-price" style={{ color: 'var(--green)' }}>
            {(market.price_yes * 100).toFixed(1)}%
          </div>
        </button>
        <button
          className={`outcome-btn ${outcome === 'no' ? 'selected-no' : ''}`}
          onClick={() => setOutcome('no')}
        >
          <div className="outcome-btn-label">No</div>
          <div className="outcome-btn-price" style={{ color: 'var(--red)' }}>
            {(market.price_no * 100).toFixed(1)}%
          </div>
        </button>
      </div>

      <div className="form-group">
        <label>Shares</label>
        <input
          type="number"
          min="1"
          max="10000"
          value={shares}
          onChange={e => setShares(Math.max(0, Number(e.target.value)))}
        />
      </div>

      <div className="cost-preview">
        <div className="cost-preview-row">
          <span>Avg price</span>
          <span>${avgPrice.toFixed(4)}</span>
        </div>
        <div className="cost-preview-row">
          <span>{action === 'buy' ? 'Total cost' : 'Proceeds'}</span>
          <span style={{ color: action === 'buy' ? 'var(--red)' : 'var(--green)' }}>
            ${Math.abs(cost).toFixed(2)}
          </span>
        </div>
        <div className="cost-preview-row">
          <span>Your balance</span>
          <span>${user.balance.toFixed(2)}</span>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <button
        className={`btn ${action === 'buy' ? 'btn-green' : 'btn-red'}`}
        style={{ width: '100%', padding: '0.8rem', fontSize: '1rem' }}
        onClick={handleTrade}
        disabled={loading || shares <= 0}
      >
        {loading ? 'Processing...' : `${action === 'buy' ? 'Buy' : 'Sell'} ${shares} ${outcome.toUpperCase()}`}
      </button>
    </div>
  )
}
