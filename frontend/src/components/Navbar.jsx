import React from 'react'
import { useAuth } from '../contexts/AuthContext'  // ✅ التأكد من import صحيح
import { UserCircleIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

const Navbar = () => {
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
    toast.success('تم تسجيل الخروج بنجاح')
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">
          مرحباً بك 👋
        </h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <UserCircleIcon className="w-8 h-8 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">
              {user?.full_name || user?.username || 'مستخدم'}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <ArrowRightOnRectangleIcon className="w-4 h-4" />
            خروج
          </button>
        </div>
      </div>
    </header>
  )
}

export default Navbar