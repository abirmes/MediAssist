import { createContext, useContext, useState, useCallback } from 'react'
import API from '../api'

const ChatContext = createContext(null)

export function ChatProvider({ children }) {
    const [isOpen, setIsOpen] = useState(false)
    const [unreadCount, setUnreadCount] = useState(0)
    const [messages, setMessages] = useState([])
    const [loading, setLoading] = useState(false)
    const [analysisData, setAnalysisData] = useState(null)

    const toggleChat = useCallback(() => {
        setIsOpen(prev => !prev)
        setUnreadCount(0)
    }, [])

    const initializeChat = useCallback(async (result, symptoms) => {
        setAnalysisData({ result, symptoms })
        setMessages([])
        setLoading(true)
        try {
            const r = await API.post('/chat/initial', {
                message: '',
                symptoms: symptoms,
                analysis_result: result
            })
            setMessages([{ id: Date.now(), role: 'assistant', content: r.data.response, timestamp: new Date() }])
            setUnreadCount(1)
        } catch {
            setMessages([{ id: Date.now(), role: 'assistant', content: `Bonjour ! Orientation recommandée : ${result.orientation}. Je suis là pour vos questions !`, timestamp: new Date() }])
            setUnreadCount(1)
        } finally {
            setLoading(false)
        }
    }, [])

    const sendMessage = useCallback(async (text) => {
        if (!text.trim()) return
        const userMsg = { id: Date.now(), role: 'user', content: text, timestamp: new Date() }
        setMessages(prev => [...prev, userMsg])
        setLoading(true)
        try {
            const history = messages.map(m => ({ role: m.role, content: m.content }))
            const r = await API.post('/chat/message', {
                message: text,
                history: history,
                symptoms: analysisData?.symptoms || [],
                analysis_result: analysisData?.result || null
            })
            setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', content: r.data.response, timestamp: new Date() }])
            if (!isOpen) setUnreadCount(prev => prev + 1)
        } catch {
            setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', content: 'Désolé, une erreur est survenue.', timestamp: new Date() }])
        } finally {
            setLoading(false)
        }
    }, [messages, analysisData, isOpen])

    return (
        <ChatContext.Provider value={{ isOpen, toggleChat, unreadCount, messages, loading, initializeChat, sendMessage }}>
            {children}
        </ChatContext.Provider>
    )
}

export const useChat = () => useContext(ChatContext)