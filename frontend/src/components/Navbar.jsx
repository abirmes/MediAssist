import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const location         = useLocation()
  const navigate         = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const links = [
    { to: '/analyze',   label: '🔍 Analyser' },
    { to: '/dashboard', label: '📊 Dashboard' },
  ]

  return (
    <nav className="bg-white border-b border-slate-100 sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/analyze" className="flex items-center gap-2">
          <span className="text-2xl">🏥</span>
          <span className="font-display font-bold text-slate-900">MediAssist</span>
          <span className="text-xs bg-medical-100 text-medical-700 px-2 py-0.5
                           rounded-full font-medium">AI</span>
        </Link>

        {/* Links */}
        <div className="flex items-center gap-1">
          {links.map(l => (
            <Link
              key={l.to} to={l.to}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === l.to
                  ? 'bg-medical-50 text-medical-700'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              {l.label}
            </Link>
          ))}

          {/* User */}
          <div className="flex items-center gap-2 ml-4 pl-4 border-l border-slate-100">
            <span className="text-sm text-slate-500 hidden sm:block">
              {user?.email}
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-slate-500 hover:text-red-500
                         transition-colors px-3 py-2 rounded-lg hover:bg-red-50"
            >
              Déconnexion
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}