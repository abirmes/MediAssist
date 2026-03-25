import { useState, useEffect } from 'react'
import API from '../api'
import Navbar from '../components/Navbar'
import ResultCard from '../components/ResultCard'
import { useChat } from '../contexts/ChatContext'

export default function Analyze() {
    const [symptoms, setSymptoms] = useState([])
    const [selected, setSelected] = useState([])
    const [search, setSearch] = useState('')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const { initializeChat } = useChat()

    useEffect(() => {
        API.get('/analysis/symptoms')
            .then(r => setSymptoms(r.data))
            .catch(() => setError('Erreur chargement des symptômes'))
    }, [])

    const filtered = symptoms
        .filter(s => s.toLowerCase().includes(search.toLowerCase()))
        .slice(0, 50)

    const toggle = sym => {
        setSelected(prev =>
            prev.includes(sym) ? prev.filter(s => s !== sym) : [...prev, sym]
        )
    }

    const analyze = async () => {
        if (selected.length === 0) {
            setError('Sélectionnez au moins un symptôme')
            return
        }
        setLoading(true)
        setError('')
        setResult(null)
        try {
            const r = await API.post('/analysis/analyze', { symptoms: selected })
            setResult(r.data)
            initializeChat(r.data, selected)
        } catch {
            setError("Erreur lors de l'analyse")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-slate-50">
            <Navbar />
            <div className="max-w-4xl mx-auto px-4 py-8">

                <div className="mb-8">
                    <h1 className="font-display text-3xl font-bold text-slate-900">
                        Analyse des symptômes
                    </h1>
                    <p className="text-slate-500 mt-1">
                        Sélectionnez vos symptômes pour obtenir une orientation médicale
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    <div className="card">
                        <h2 className="font-semibold text-slate-800 mb-4">
                            Symptômes disponibles
                        </h2>
                        <input
                            type="text" value={search}
                            onChange={e => setSearch(e.target.value)}
                            placeholder="Rechercher un symptôme..."
                            className="input mb-4"
                        />
                        <div className="h-80 overflow-y-auto space-y-1 pr-1">
                            {filtered.map(sym => (
                                <button
                                    key={sym}
                                    onClick={() => toggle(sym)}
                                    className={`w-full text-left px-3 py-2 rounded-lg text-sm
                                        transition-all duration-150 ${selected.includes(sym)
                                            ? 'bg-medical-100 text-medical-700 font-medium'
                                            : 'hover:bg-slate-100 text-slate-700'
                                        }`}
                                >
                                    {selected.includes(sym) ? '✓ ' : ''}{sym}
                                </button>
                            ))}
                            {filtered.length === 0 && (
                                <p className="text-slate-400 text-sm text-center py-8">
                                    Aucun symptôme trouvé
                                </p>
                            )}
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="card">
                            <h2 className="font-semibold text-slate-800 mb-4">
                                Vos symptômes ({selected.length})
                            </h2>

                            {selected.length === 0 ? (
                                <p className="text-slate-400 text-sm text-center py-8">
                                    Aucun symptôme sélectionné
                                </p>
                            ) : (
                                <div className="flex flex-wrap gap-2 mb-4">
                                    {selected.map(sym => (
                                        <span key={sym}
                                            className="inline-flex items-center gap-1 bg-medical-100
                                                text-medical-700 text-sm px-3 py-1 rounded-full">
                                            {sym}
                                            <button onClick={() => toggle(sym)}
                                                className="hover:text-red-500 ml-1 font-bold">×</button>
                                        </span>
                                    ))}
                                </div>
                            )}

                            {error && (
                                <div className="bg-red-50 text-red-600 rounded-xl px-4 py-3 text-sm mb-4">
                                    {error}
                                </div>
                            )}

                            <button onClick={analyze}
                                disabled={loading || selected.length === 0}
                                className="btn-primary w-full">
                                {loading ? (
                                    <span className="flex items-center justify-center gap-2">
                                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                                            <circle className="opacity-25" cx="12" cy="12" r="10"
                                                stroke="currentColor" strokeWidth="4" />
                                            <path className="opacity-75" fill="currentColor"
                                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                        </svg>
                                        Analyse en cours...
                                    </span>
                                ) : '🔍 Analyser mes symptômes'}
                            </button>
                        </div>

                        {result && (
                            <>
                                <ResultCard result={result} />
                                <div className="bg-medical-50 border border-medical-200
                                    rounded-xl px-4 py-3 flex items-center gap-3">
                                    <span className="text-xl">💬</span>
                                    <p className="text-medical-700 text-sm">
                                        L'assistant a analysé vos résultats.
                                        <strong> Cliquez sur le bouton chat</strong> en bas à droite !
                                    </p>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}