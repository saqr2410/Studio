import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  HomeIcon,
  DocumentTextIcon,
  CalendarIcon,
  UsersIcon,
  CreditCardIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'

const menuItems = [
  { path: '/', icon: HomeIcon, label: 'الرئيسية' },
  { path: '/reports', icon: DocumentTextIcon, label: 'التقارير' },
  { path: '/bookings', icon: CalendarIcon, label: 'الحجوزات' },
  { path: '/customers', icon: UsersIcon, label: 'العملاء' },
  { path: '/users', icon: UserGroupIcon, label: 'المستخدمين' },
  { path: '/payments', icon: CreditCardIcon, label: 'المدفوعات' },
  { path: '/finance', icon: ChartBarIcon, label: 'المالية' },
]

const Sidebar = () => {
  return (
    <div className="w-64 bg-white border-l border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-primary-600">📸 استوديو</h1>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-200">
        <button className="flex items-center gap-3 w-full px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
          <Cog6ToothIcon className="w-5 h-5" />
          <span>الإعدادات</span>
        </button>
      </div>
    </div>
  )
}

export default Sidebar