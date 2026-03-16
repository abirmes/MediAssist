import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Register() {
    const { register } = useAuth()
    const navigate = useNavigate()
    const [email, setEmail] = useState('')
    const [password, setPass] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async e => {
        e.preventDefault()
        setError('')
        if (password.length < 6) {
            setError('Le mot de passe doit contenir au moins 6 caractères')
            return
        }
        setLoading(true)
        try {
            await register(email, password)
            navigate('/analyze')
        } catch (err) {
            setError(err.response?.data?.detail || 'Erreur lors de l\'inscription')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-medical-50 to-slate-100
                    flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16
                          bg-medical-600 rounded-2xl shadow-lg mb-4">
                        <span className="text-3xl">🏥</span>
                    </div>
                    <h1 className="font-display text-3xl font-bold text-slate-900">
                        MediAssist AI
                    </h1>
                    <p className="text-slate-500 mt-1">Créez votre compte gratuitement</p>
                </div>

                <div className="card">
                    <h2 className="font-display text-xl font-semibold mb-6">Inscription</h2>

                    {error && (
                        <div className="bg-red-50 text-red-600 rounded-xl px-4 py-3 mb-4 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">
                                Email
                            </label>
                            <input
                                type="email" value={email}
                                onChange={e => setEmail(e.target.value)}
                                className="input" placeholder="vous@exemple.com" required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">
                                Mot de passe
                            </label>
                            <input
                                type="password" value={password}
                                onChange={e => setPass(e.target.value)}
                                className="input" placeholder="Min. 6 caractères" required
                            />
                        </div>
                        <button type="submit" className="btn-primary w-full" disabled={loading}>
                            {loading ? 'Création...' : 'Créer mon compte'}
                        </button>
                    </form>

                    <p className="text-center text-sm text-slate-500 mt-4">
                        Déjà un compte ?{' '}
                        <Link to="/login" className="text-medical-600 font-medium hover:underline">
                            Se connecter
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    )
}