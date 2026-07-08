import React from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calendar,
  Users,
  Camera,
  Clock,
  CheckCircle,
  AlertCircle,
  MoreHorizontal,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from 'recharts'

const COLORS = ['#6366f1', '#4f46e5', '#818cf8', '#a5b4fc', '#c7d2fe']

const Dashboard = () => {
  // ✅ جلب جميع البيانات من الـ API
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const [finance, bookings, customers, payments] = await Promise.all([
        api.get('/finance/'),
        api.get('/bookings/'),
        api.get('/customers/'),
        api.get('/payments/'),
      ])
      return {
        finance: finance.data,
        bookings: bookings.data,
        customers: customers.data,
        payments: payments.data,
      }
    },
    refetchOnWindowFocus: true,
    staleTime: 0,
  })

  if (isLoading) return <LoadingSpinner />

  // ✅ بيانات حقيقية من الـ API
  const totalIncome = stats?.finance?.total_income || 0
  const totalExpenses = stats?.finance?.total_expenses || 0
  const profit = stats?.finance?.profit || 0
  
  // ✅ الحجوزات
  const bookingsList = stats?.bookings?.results || []
  const totalBookings = stats?.bookings?.count || bookingsList.length
  
  // ✅ العملاء
  const customersList = stats?.customers?.results || []
  const totalCustomers = stats?.customers?.count || customersList.length
  
  // ✅ المدفوعات
  const paymentsList = stats?.payments?.results || []
  const totalPayments = stats?.payments?.count || paymentsList.length

  // ✅ إحصائيات الحجوزات
  const confirmedCount = bookingsList.filter(b => b.status === 'confirmed' || b.status === 'confirmed').length
  const pendingCount = bookingsList.filter(b => b.status === 'pending').length
  const doneCount = bookingsList.filter(b => b.status === 'done').length
  const cancelledCount = bookingsList.filter(b => b.status === 'cancelled').length

  // ✅ بيانات حالة الحجوزات للـ Pie Chart
  const bookingStatusData = [
    { name: 'مؤكد', value: confirmedCount || 1 },
    { name: 'قيد الانتظار', value: pendingCount || 1 },
    { name: 'منتهي', value: doneCount || 1 },
    { name: 'ملغي', value: cancelledCount || 1 },
  ].filter(item => item.value > 0)

  // ✅ آخر 5 حجوزات من البيانات الفعلية
  const recentBookings = bookingsList.slice(0, 5).map(booking => ({
    id: booking.id,
    customer: booking.customer_name || booking.customer || 'عميل',
    date: booking.date || '2026-07-08',
    amount: booking.price || 0,
    status: booking.status || 'pending',
  }))

  // ✅ بيانات الشارت الشهرية (لو موجودة في الـ API)
  const monthlyData = stats?.finance?.monthly_data || [
    { month: 'يناير', income: 0, expenses: 0 },
    { month: 'فبراير', income: 0, expenses: 0 },
    { month: 'مارس', income: 0, expenses: 0 },
    { month: 'أبريل', income: 0, expenses: 0 },
    { month: 'مايو', income: 0, expenses: 0 },
    { month: 'يونيو', income: 0, expenses: 0 },
  ]

  // ✅ حساب نسبة التغير
  const profitMargin = totalIncome > 0 ? ((profit / totalIncome) * 100).toFixed(1) : 0

  const getStatusBadge = (status) => {
    const badges = {
      confirmed: 'bg-green-100 text-green-700',
      pending: 'bg-yellow-100 text-yellow-700',
      done: 'bg-blue-100 text-blue-700',
      cancelled: 'bg-red-100 text-red-700',
      in_progress: 'bg-purple-100 text-purple-700',
      no_show: 'bg-gray-100 text-gray-700',
    }
    return badges[status] || 'bg-gray-100 text-gray-700'
  }

  const getStatusText = (status) => {
    const texts = {
      confirmed: 'مؤكد',
      pending: 'قيد الانتظار',
      done: 'منتهي',
      cancelled: 'ملغي',
      in_progress: 'قيد التنفيذ',
      no_show: 'لم يحضر',
    }
    return texts[status] || status
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">لوحة التحكم</h1>
          <p className="text-gray-500 mt-1">مرحباً بك في لوحة تحكم الاستوديو</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            اليوم
          </button>
          <button className="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            تصدير
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-500">إجمالي الإيرادات</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{totalIncome.toLocaleString()} ج.م</p>
              <p className="text-sm text-green-600 mt-1 flex items-center gap-1">
                <ArrowUpRight className="w-4 h-4" />
                +{profitMargin}%
              </p>
            </div>
            <div className="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-500">إجمالي المصروفات</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{totalExpenses.toLocaleString()} ج.م</p>
              <p className="text-sm text-red-600 mt-1 flex items-center gap-1">
                <ArrowDownRight className="w-4 h-4" />
                -{totalExpenses > 0 ? ((totalExpenses / (totalIncome + totalExpenses)) * 100).toFixed(1) : 0}%
              </p>
            </div>
            <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center">
              <TrendingDown className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-500">صافي الأرباح</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{profit.toLocaleString()} ج.م</p>
              <p className={`text-sm mt-1 flex items-center gap-1 ${profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {profit >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                {profit >= 0 ? '+' : ''}{profitMargin}%
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-500">عدد الحجوزات</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{totalBookings}</p>
              <p className="text-sm text-blue-600 mt-1 flex items-center gap-1">
                <ArrowUpRight className="w-4 h-4" />
                +{bookingsList.length > 0 ? ((confirmedCount / bookingsList.length) * 100).toFixed(1) : 0}% مؤكد
              </p>
            </div>
            <div className="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center">
              <Calendar className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Income vs Expenses Chart */}
        <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-900">الإيرادات والمصروفات</h3>
            <button className="text-gray-400 hover:text-gray-600">
              <MoreHorizontal className="w-5 h-5" />
            </button>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyData}>
                <defs>
                  <linearGradient id="incomeGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="expenseGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="income"
                  stroke="#6366f1"
                  fill="url(#incomeGradient)"
                  name="الإيرادات"
                />
                <Area
                  type="monotone"
                  dataKey="expenses"
                  stroke="#ef4444"
                  fill="url(#expenseGradient)"
                  name="المصروفات"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Booking Status Chart */}
        <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-900">حالة الحجوزات</h3>
            <button className="text-gray-400 hover:text-gray-600">
              <MoreHorizontal className="w-5 h-5" />
            </button>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={bookingStatusData.length > 0 ? bookingStatusData : [{ name: 'لا توجد بيانات', value: 1 }]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={100}
                  dataKey="value"
                >
                  {bookingStatusData.length > 0 ? (
                    bookingStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))
                  ) : (
                    <Cell fill="#e5e7eb" />
                  )}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Bookings & Quick Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Bookings Table */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-900">آخر الحجوزات</h3>
            <button className="text-sm text-primary-600 hover:text-primary-700">عرض الكل</button>
          </div>
          {recentBookings.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-right py-3 text-xs font-medium text-gray-500 uppercase">العميل</th>
                    <th className="text-right py-3 text-xs font-medium text-gray-500 uppercase">التاريخ</th>
                    <th className="text-right py-3 text-xs font-medium text-gray-500 uppercase">المبلغ</th>
                    <th className="text-right py-3 text-xs font-medium text-gray-500 uppercase">الحالة</th>
                  </tr>
                </thead>
                <tbody>
                  {recentBookings.map((booking) => (
                    <tr key={booking.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                      <td className="py-3 text-sm font-medium text-gray-900">{booking.customer}</td>
                      <td className="py-3 text-sm text-gray-600">{booking.date}</td>
                      <td className="py-3 text-sm font-medium text-gray-900">{booking.amount} ج.م</td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(booking.status)}`}>
                          {getStatusText(booking.status)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>لا توجد حجوزات لعرضها</p>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 space-y-4">
          <h3 className="font-semibold text-gray-900">إحصائيات سريعة</h3>

          <div className="flex items-center justify-between p-3 bg-green-50 rounded-xl">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-sm text-gray-700">حجوزات مؤكدة</span>
            </div>
            <span className="font-bold text-green-700">{confirmedCount}</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-xl">
            <div className="flex items-center gap-3">
              <Clock className="w-5 h-5 text-yellow-600" />
              <span className="text-sm text-gray-700">قيد الانتظار</span>
            </div>
            <span className="font-bold text-yellow-700">{pendingCount}</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-xl">
            <div className="flex items-center gap-3">
              <Users className="w-5 h-5 text-blue-600" />
              <span className="text-sm text-gray-700">إجمالي العملاء</span>
            </div>
            <span className="font-bold text-blue-700">{totalCustomers}</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-purple-50 rounded-xl">
            <div className="flex items-center gap-3">
              <Camera className="w-5 h-5 text-purple-600" />
              <span className="text-sm text-gray-700">حجوزات منتهية</span>
            </div>
            <span className="font-bold text-purple-700">{doneCount}</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-red-50 rounded-xl">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="text-sm text-gray-700">حجوزات ملغية</span>
            </div>
            <span className="font-bold text-red-700">{cancelledCount}</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-indigo-50 rounded-xl">
            <div className="flex items-center gap-3">
              <DollarSign className="w-5 h-5 text-indigo-600" />
              <span className="text-sm text-gray-700">إجمالي المدفوعات</span>
            </div>
            <span className="font-bold text-indigo-700">{totalPayments}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard