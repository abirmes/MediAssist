import { createContext, useContext, useState, useEffect } from 'react'
import API from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const token = localStorage.getItem('token')
        if (token) {
            API.get('/auth/me')
                .then(r => setUser(r.data))
                .catch(() => localStorage.removeItem('token'))
                .finally(() => setLoading(false))
        } else {
            setLoading(false)
        }
    }, [])

    const login = async (email, password) => {
        const r = await API.post('/auth/login', { email, password })
        localStorage.setItem('token', r.data.access_token)
        const me = await API.get('/auth/me')
        setUser(me.data)
    }

    const register = async (email, password) => {
        await API.post('/auth/register', { email, password })
        await login(email, password)
    }

    const logout = () => {
        localStorage.removeItem('token')
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)