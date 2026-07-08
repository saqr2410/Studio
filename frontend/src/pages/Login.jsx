import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import api from '../api/axios'
import { useAuth } from '../contexts/AuthContext'

const Login = () => {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()  // ✅ استخدم login من Context

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    console.log('🔐 محاولة تسجيل الدخول:', username)
    
    try {
      // ✅ استخدم login من Context عشان يخزن التوكن ويجيب المستخدم
      await login(username.trim(), password.trim())
      
      console.log('✅ تم تسجيل الدخول بنجاح')
      toast.success('تم تسجيل الدخول بنجاح 🎉')
      
      // ✅ حول للـ Dashboard
      navigate('/')
      
    } catch (error) {
      console.error('❌ خطأ:', error)
      
      if (error.code === 'ERR_NETWORK') {
        toast.error('لا يمكن الاتصال بالخادم، تأكد من تشغيل Django')
      } else if (error.response?.data?.detail) {
        toast.error(error.response.data.detail)
      } else if (error.response?.status === 401) {
        toast.error('اسم المستخدم أو كلمة المرور غير صحيحة')
      } else {
        toast.error('حدث خطأ غير متوقع')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-blue-50">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-600">📸 استوديو</h1>
          <p className="text-gray-600 mt-2">نظام إدارة الاستوديو</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="label">اسم المستخدم</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input"
              placeholder="أدخل اسم المستخدم"
              required
            />
          </div>
          
          <div>
            <label className="label">كلمة المرور</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              placeholder="أدخل كلمة المرور"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-3 text-lg disabled:opacity-50"
          >
            {loading ? 'جاري تسجيل الدخول...' : 'تسجيل الدخول'}
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>👤 admin / admin123</p>
        </div>
      </div>
    </div>
  )
}

export default Login