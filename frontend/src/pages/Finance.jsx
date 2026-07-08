import React from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import StatsCard from '../components/StatsCard'
import toast from 'react-hot-toast'
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
} from 'recharts'

const COLORS = ['#6366f1', '#4f46e5', '#818cf8', '#a5b4fc']

const Finance = () => {
  const queryClient = useQueryClient()

  const { data: finance, isLoading } = useQuery({
    queryKey: ['finance-summary'],
    queryFn: async () => {
      const response = await api.get('/finance/')
      console.log('📊 Finance data:', response.data)
      return response.data
    },
    refetchOnWindowFocus: true,
    staleTime: 0,
  })

  const { data: monthlyData } = useQuery({
    queryKey: ['finance-monthly'],
    queryFn: async () => {
      const response = await api.get('/finance/monthly/')
      console.log('📈 Monthly data:', response.data)
      return response.data
    },
    refetchOnWindowFocus: true,
    staleTime: 0,
  })

  const refreshData = () => {
    queryClient.invalidateQueries(['finance-summary'])
    queryClient.invalidateQueries(['finance-monthly'])
    toast.success('🔄 تم تحديث البيانات المالية')
  }

  if (isLoading) return <LoadingSpinner />

  const expenseData = Object.entries(finance?.expenses_by_category || {}).map(([key, value]) => ({
    name: key,
    value: Number(value),
  }))

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">المالية</h1>
        <button
          onClick={refreshData}
          className="btn-secondary text-sm flex items-center gap-2"
        >
          🔄 تحديث البيانات
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatsCard
          title="إجمالي الإيرادات"
          value={`${finance?.total_income || 0} ج.م`}
          icon="💰"
          color="bg-green-500"
        />
        <StatsCard
          title="إجمالي المصروفات"
          value={`${finance?.total_expenses || 0} ج.م`}
          icon="💳"
          color="bg-red-500"
        />
        <StatsCard
          title="الأرباح"
          value={`${finance?.profit || 0} ج.م`}
          icon="📈"
          color="bg-blue-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold mb-4">الإيرادات والمصروفات الشهرية</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyData || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="income" fill="#6366f1" name="الإيرادات" />
                <Bar dataKey="expenses" fill="#ef4444" name="المصروفات" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold mb-4">توزيع المصروفات</h3>
          <div className="h-80">
            {expenseData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={expenseData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {expenseData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                لا توجد بيانات
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Finance