const ORIENTATION_CONFIG = {
    urgences: {
        icon: '🚨',
        label: 'Urgences',
        color: 'text-red-700',
        bg: 'bg-red-50',
        border: 'border-red-200',
        action: 'Appelez le 15 (SAMU) immédiatement',
    },
    medecin: {
        icon: '👨‍⚕️',
        label: 'Consultez un médecin',
        color: 'text-amber-700',
        bg: 'bg-amber-50',
        border: 'border-amber-200',
        action: 'Prenez rendez-vous dans les 24-48h',
    },
    surveillance: {
        icon: '🏠',
        label: 'Surveillance à domicile',
        color: 'text-green-700',
        bg: 'bg-green-50',
        border: 'border-green-200',
        action: 'Surveillez vos symptômes et reposez-vous',
    },
}

const RISK_CONFIG = {
    critical: { label: 'Critique', color: 'bg-red-500' },
    high: { label: 'Élevé', color: 'bg-orange-500' },
    medium: { label: 'Modéré', color: 'bg-amber-400' },
    low: { label: 'Faible', color: 'bg-green-500' },
}

export default function ResultCard({ result }) {
    const cfg = ORIENTATION_CONFIG[result.orientation] || ORIENTATION_CONFIG.medecin
    const risk = RISK_CONFIG[result.risk_level] || RISK_CONFIG.medium

    return (
        <div className={`card border-2 ${cfg.border} ${cfg.bg}`}>
            {/* Header */}
            <div className="flex items-center gap-3 mb-4">
                <span className="text-4xl">{cfg.icon}</span>
                <div>
                    <h3 className={`font-display text-xl font-bold ${cfg.color}`}>
                        {cfg.label}
                    </h3>
                    <p className="text-slate-600 text-sm">{cfg.action}</p>
                </div>
            </div>

            {/* Score */}
            <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-600">Score de gravité</span>
                    <span className="font-semibold">{result.severity_score}/100</span>
                </div>
                <div className="w-full bg-white rounded-full h-2.5">
                    <div
                        className={`h-2.5 rounded-full ${risk.color} transition-all duration-700`}
                        style={{ width: `${result.severity_score}%` }}
                    />
                </div>
                <div className="flex justify-between text-xs mt-1">
                    <span className="text-slate-400">Niveau : {risk.label}</span>
                </div>
            </div>

            {/* Explication */}
            {result.explanation && (
                <div className="bg-white bg-opacity-70 rounded-xl p-4 text-sm
                        text-slate-700 leading-relaxed mb-3">
                    {result.explanation}
                </div>
            )}

            {/* Disclaimer */}
            <p className="text-xs text-slate-500 text-center">
                ⚠️ Ce résultat est indicatif et ne remplace pas un avis médical professionnel
            </p>
        </div>
    )
}