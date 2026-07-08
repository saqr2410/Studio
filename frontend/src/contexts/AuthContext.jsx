import React, { createContext, useState, useContext, useEffect } from 'react'
import api from '../api/axios'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      console.log('🔍 جلب بيانات المستخدم...')
      const response = await api.get('/users/me/')
      console.log('✅ بيانات المستخدم:', response.data)
      setUser(response.data)
    } catch (error) {
      console.error('❌ خطأ في جلب المستخدم:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    console.log('🔐 محاولة تسجيل الدخول...')
    const response = await api.post('/token/', { username, password })
    console.log('✅ توكن:', response.data.access)
    
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    
    console.log('🔍 جلب بيانات المستخدم بعد تسجيل الدخول...')
    await fetchUser()
    
    console.log('✅ تم تسجيل الدخول بنجاح')
    return response.data
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}