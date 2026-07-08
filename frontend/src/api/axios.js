import axios from 'axios'
import toast from 'react-hot-toast'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',  // ✅ استخدم الـ URL الكامل
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 30000,
})

// ✅ Interceptor لإضافة التوكن
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
    
    console.log('🚀 Request:', config.method.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        console.log("Status:", error.response?.status);
        console.log("Data:", error.response?.data);
        console.log("Full Error:", error.response);

        return Promise.reject(error);
      }
    );
    return response
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.status, error.response?.data)
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