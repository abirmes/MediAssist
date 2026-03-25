import { useChat } from '../contexts/ChatContext'
import ChatSidebar from './ChatSidebar'

export default function ChatBot() {
    const { toggleChat, unread, isOpen } = useChat()

    return (
        <>
            <ChatSidebar />

            {/* Bouton flottant */}
            <button
                onClick={toggleChat}
                className="fixed bottom-4 right-4 z-50
                   bg-medical-600 hover:bg-medical-700
                   text-white rounded-full w-14 h-14
                   shadow-lg hover:shadow-xl
                   transition-all duration-200
                   flex items-center justify-center
                   hover:scale-110"
                title="Ouvrir le chatbot médical"
            >
                {isOpen ? (
                    <span className="text-xl">✕</span>
                ) : (
                    <span className="text-2xl">💬</span>
                )}

                {/* Badge notifications */}
                {unread > 0 && !isOpen && (
                    <span className="absolute -top-1 -right-1
                           bg-red-500 text-white text-xs font-bold
                           w-5 h-5 rounded-full
                           flex items-center justify-center
                           animate-pulse">
                        {unread}
                    </span>
                )}
            </button>
        </>
    )
}