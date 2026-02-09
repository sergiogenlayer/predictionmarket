import { useNavigate } from 'react-router-dom'

export default function MarketCard({ market }) {
  const navigate = useNavigate()
  const yesPercent = (market.price_yes * 100).toFixed(0)
  const noPercent = (market.price_no * 100).toFixed(0)
  const resDate = new Date(market.resolution_date).toLocaleDateString()

  return (
    <div className="card market-card" onClick={() => navigate(`/market/${market.id}`)}>
      <div className="market-card-title">{market.title}</div>

      <div className="price-bar">
        <div className="price-bar-fill" style={{ width: `${yesPercent}%` }} />
      </div>

      <div className="price-labels">
        <span className="price-yes">Yes {yesPercent}%</span>
        <span className="price-no">No {noPercent}%</span>
      </div>

      <div className="market-card-meta">
        <span>
          {market.resolved ? (
            <span className={`badge ${market.outcome ? 'badge-yes' : 'badge-no'}`}>
              Resolved {market.outcome ? 'YES' : 'NO'}
            </span>
          ) : (
            <span className="badge badge-active">Active</span>
          )}
        </span>
        <span>Resolves: {resDate}</span>
        {market.total_volume > 0 && (
          <span className="volume-text">${market.total_volume.toFixed(0)} vol</span>
        )}
      </div>
    </div>
  )
}
