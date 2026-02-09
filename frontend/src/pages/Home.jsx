import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { fetchAPI } from '../api'
import { useAuth } from '../context/AuthContext'
import MarketCard from '../components/MarketCard'

export default function Home() {
  const { user } = useAuth()
  const [markets, setMarkets] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadMarkets()
  }, [filter])

  const loadMarkets = async () => {
    try {
      const params = new URLSearchParams()
      if (filter !== 'all') params.set('status', filter)
      if (search) params.set('search', search)
      const data = await fetchAPI(`/markets?${params.toString()}`)
      setMarkets(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    setSearch(e.target.value)
  }

  useEffect(() => {
    const timer = setTimeout(loadMarkets, 300)
    return () => clearTimeout(timer)
  }, [search])

  const filteredMarkets = markets

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Markets</h1>
        {user && (
          <Link to="/create" className="btn btn-primary">
            + New Market
          </Link>
        )}
      </div>

      <div className="filters">
        <input
          className="search-input"
          type="text"
          placeholder="Search markets..."
          value={search}
          onChange={handleSearch}
        />
        {['all', 'active', 'resolved'].map(f => (
          <button
            key={f}
            className={`filter-btn ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem' }}>
          Loading markets...
        </p>
      ) : filteredMarkets.length === 0 ? (
        <div className="empty-state">
          <p>No markets found</p>
          {user && (
            <Link to="/create" className="btn btn-primary">Create the first market</Link>
          )}
        </div>
      ) : (
        <div className="markets-grid">
          {filteredMarkets.map(m => (
            <MarketCard key={m.id} market={m} />
          ))}
        </div>
      )}
    </div>
  )
}
