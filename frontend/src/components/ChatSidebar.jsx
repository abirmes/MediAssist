import { useState, useEffect, useRef } from 'react'
import { useChat } from '../contexts/ChatContext'

export default function ChatSidebar() {
    const { isOpen, toggleChat, messages, loading, sendMessage, clearChat } = useChat()
    const [input, setInput] = useState('')
    const bottomRef = useRef(null)

    // Auto-scroll vers le bas
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, loading])

    const handleSend = async () => {
        if (!input.trim() || loading) return
        const text = input
        setInput('')
        await sendMessage(text)
    }

    const handleKey = e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    if (!isOpen) return null

    return (
        <>
            {/* Overlay mobile */}
            <div
                className="fixed inset-0 bg-black bg-opacity-20 z-40 lg:hidden"
                onClick={toggleChat}
            />

            {/* Sidebar */}
            <div className="fixed bottom-20 right-4 z-50 w-80 sm:w-96
                      bg-white rounded-2xl shadow-2xl border border-slate-100
                      flex flex-col overflow-hidden"
                style={{ height: '480px' }}>

                {/* Header */}
                <div className="bg-medical-600 px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="text-xl">🏥</span>
                        <div>
                            <p className="text-white font-semibold text-sm">MediBot</p>
                            <p className="text-medical-200 text-xs">Assistant médical IA</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={clearChat}
                            className="text-medical-200 hover:text-white text-xs px-2 py-1
                         rounded-lg hover:bg-medical-700 transition-colors"
                        >
                            Effacer
                        </button>
                        <button
                            onClick={toggleChat}
                            className="text-white hover:text-medical-200 transition-colors text-lg"
                        >
                            ✕
                        </button>
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50">
                    {messages.length === 0 && (
                        <div className="text-center text-slate-400 text-sm py-8">
                            <p className="text-2xl mb-2">💬</p>
                            <p>Analysez vos symptômes pour démarrer</p>
                        </div>
                    )}

                    {messages.map((msg, i) => (
                        <div key={i}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] px-3 py-2 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                                    ? 'bg-medical-600 text-white rounded-br-sm'
                                    : msg.is_auto
                                        ? 'bg-amber-50 text-amber-900 border border-amber-200 rounded-bl-sm'
                                        : 'bg-white text-slate-700 shadow-sm rounded-bl-sm'
                                }`}>
                                {msg.is_auto && (
                                    <p className="text-xs text-amber-600 font-medium mb-1">
                                        🤖 Analyse automatique
                                    </p>
                                )}
                                <p className="whitespace-pre-wrap">{msg.content}</p>
                                <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-medical-200' : 'text-slate-400'
                                    }`}>
                                    {new Date(msg.timestamp).toLocaleTimeString('fr-FR', {
                                        hour: '2-digit', minute: '2-digit'
                                    })}
                                </p>
                            </div>
                        </div>
                    ))}

                    {/* Loading */}
                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                                <div className="flex gap-1">
                                    <span className="w-2 h-2 bg-medical-400 rounded-full animate-bounce"
                                        style={{ animationDelay: '0ms' }} />
                                    <span className="w-2 h-2 bg-medical-400 rounded-full animate-bounce"
                                        style={{ animationDelay: '150ms' }} />
                                    <span className="w-2 h-2 bg-medical-400 rounded-full animate-bounce"
                                        style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={bottomRef} />
                </div>

                {/* Input */}
                <div className="p-3 border-t border-slate-100 bg-white">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={handleKey}
                            placeholder="Posez votre question..."
                            disabled={loading}
                            className="flex-1 border border-slate-200 rounded-xl px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-medical-500
                         disabled:opacity-50"
                        />
                        <button
                            onClick={handleSend}
                            disabled={loading || !input.trim()}
                            className="bg-medical-600 text-white px-3 py-2 rounded-xl
                         hover:bg-medical-700 transition-colors
                         disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            ➤
                        </button>
                    </div>
                    <p className="text-xs text-slate-400 text-center mt-2">
                        ⚠️ Ne remplace pas un avis médical
                    </p>
                </div>
            </div>
        </>
    )
}