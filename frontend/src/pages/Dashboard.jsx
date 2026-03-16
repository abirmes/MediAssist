import { useState, useEffect } from 'react'
import API from '../api'
import Navbar from '../components/Navbar'

export default function Dashboard() {
    const [stats, setStats] = useState(null)
    const [history, setHistory] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        Promise.all([
            API.get('/dashboard/stats'),
            API.get('/analysis/history')
        ]).then(([s, h]) => {
            setStats(s.data)
            setHistory(h.data)
        }).finally(() => setLoading(false))
    }, [])

    if (loading) return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center">
            <div className="animate-spin h-8 w-8 border-4 border-medical-500
                      border-t-transparent rounded-full"/>
        </div>
    )

    const orientationConfig = {
        urgences: { icon: '🚨', color: 'text-red-600', bg: 'bg-red-50', label: 'Urgences' },
        medecin: { icon: '👨‍⚕️', color: 'text-amber-600', bg: 'bg-amber-50', label: 'Médecin' },
        surveillance: { icon: '🏠', color: 'text-green-600', bg: 'bg-green-50', label: 'Surveillance' },
    }

    return (
        <div className="min-h-screen bg-slate-50">
            <Navbar />
            <div className="max-w-4xl mx-auto px-4 py-8">

                <h1 className="font-display text-3xl font-bold text-slate-900 mb-8">
                    Tableau de bord
                </h1>

                {/* Stats */}
                {stats && (
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                        {[
                            { label: 'Total', value: stats.total_consultations, icon: '📋', color: 'text-slate-700' },
                            { label: 'Urgences', value: stats.urgences_count, icon: '🚨', color: 'text-red-600' },
                            { label: 'Médecin', value: stats.medecin_count, icon: '👨‍⚕️', color: 'text-amber-600' },
                            { label: 'Surveillance', value: stats.surveillance_count, icon: '🏠', color: 'text-green-600' },
                        ].map(s => (
                            <div key={s.label} className="card text-center">
                                <div className="text-2xl mb-1">{s.icon}</div>
                                <div className={`font-display text-3xl font-bold ${s.color}`}>
                                    {s.value}
                                </div>
                                <div className="text-slate-500 text-sm">{s.label}</div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Score moyen */}
                {stats && (
                    <div className="card mb-8">
                        <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-slate-700">Score de gravité moyen</span>
                            <span className="font-display text-2xl font-bold text-medical-600">
                                {stats.avg_severity_score}/100
                            </span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-3">
                            <div
                                className="h-3 rounded-full bg-gradient-to-r from-green-400
                           via-amber-400 to-red-500 transition-all duration-700"
                                style={{ width: `${stats.avg_severity_score}%` }}
                            />
                        </div>
                    </div>
                )}

                {/* Historique */}
                <div className="card">
                    <h2 className="font-semibold text-slate-800 mb-4">
                        Historique des consultations
                    </h2>

                    {history.length === 0 ? (
                        <p className="text-slate-400 text-center py-8">
                            Aucune consultation pour l'instant
                        </p>
                    ) : (
                        <div className="space-y-3">
                            {history.map(c => {
                                const cfg = orientationConfig[c.analysis?.orientation] ||
                                    orientationConfig.medecin
                                return (
                                    <div key={c.id}
                                        className="flex items-center justify-between p-4
                                  bg-slate-50 rounded-xl hover:bg-slate-100
                                  transition-colors">
                                        <div className="flex items-center gap-3">
                                            <span className={`text-xl px-3 py-2 rounded-lg ${cfg.bg}`}>
                                                {cfg.icon}
                                            </span>
                                            <div>
                                                <p className="font-medium text-slate-800 text-sm">
                                                    {c.raw_input?.slice(0, 50)}...
                                                </p>
                                                <p className="text-slate-400 text-xs">
                                                    {new Date(c.date).toLocaleDateString('fr-FR', {
                                                        day: '2-digit', month: 'long', year: 'numeric'
                                                    })}
                                                </p>
                                            </div>
                                        </div>
                                        {c.analysis && (
                                            <div className="text-right">
                                                <span className={`text-sm font-semibold ${cfg.color}`}>
                                                    {cfg.label}
                                                </span>
                                                <p className="text-slate-400 text-xs">
                                                    Score: {c.analysis.severity_score}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}