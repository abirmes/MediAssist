import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login     from './pages/Login'
import Register  from './pages/Register'
import Analyze   from './pages/Analyze'
import Dashboard from './pages/Dashboard'

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin h-8 w-8 border-4 border-medical-500
                      border-t-transparent rounded-full"/>
    </div>
  )
  return user ? children : <Navigate to="/login" />
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login"    element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/analyze"  element={
            <PrivateRoute><Analyze /></PrivateRoute>
          }/>
          <Route path="/dashboard" element={
            <PrivateRoute><Dashboard /></PrivateRoute>
          }/>
          <Route path="*" element={<Navigate to="/analyze" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}