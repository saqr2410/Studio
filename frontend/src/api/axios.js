import axios from 'axios'
import toast from 'react-hot-toast'

const api = axios.create({
  baseURL: 'https://mohamed2410.pythonanywhere.com/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 30000,
})

// ✅ إضافة التوكن مع كل Request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')

    console.log('🔑 Token in request:', token ? 'Yes' : 'No')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('✅ Authorization header added')
    } else {
      console.log('⚠️ No token found')
    }

    console.log(
      '🚀 Request:',
      config.method?.toUpperCase(),
      config.url
    )

    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)


// ✅ التعامل مع Response والأخطاء
api.interceptors.response.use(
  (response) => {
    return response
  },

  (error) => {
    console.error(
      '❌ Response Error:',
      error.response?.status,
      error.response?.data
    )

    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')

      window.location.href = '/login'

      toast.error('انتهت الجلسة، يرجى تسجيل الدخول مرة أخرى')
    }

    return Promise.reject(error)
  }
)


export default api