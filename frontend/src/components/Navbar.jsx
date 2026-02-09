import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        Prediction Market
      </Link>

      <div className="navbar-links">
        <Link to="/">Markets</Link>
        {user && <Link to="/create">Create</Link>}
        {user && <Link to="/portfolio">Portfolio</Link>}
      </div>

      <div className="navbar-user">
        {user ? (
          <>
            <span className="navbar-balance">${user.balance.toFixed(2)}</span>
            <span className="navbar-username">{user.username}</span>
            <button className="btn btn-outline btn-sm" onClick={logout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="btn btn-outline btn-sm">Login</Link>
            <Link to="/register" className="btn btn-primary btn-sm">Register</Link>
          </>
        )}
      </div>
    </nav>
  )
}
