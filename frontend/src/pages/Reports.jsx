import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import { Link } from 'react-router-dom'
import api from '../api/axios'
import toast from 'react-hot-toast'
import LoadingSpinner from '../components/LoadingSpinner'
import { format } from 'date-fns'
import { ar } from 'date-fns/locale'

const Reports = () => {
  const [selectedStatus, setSelectedStatus] = useState('')
  const queryClient = useQueryClient()

  const { data: reports, isLoading } = useQuery('reports', async () => {
    const response = await api.get('/reports/reports/')
    return response.data
  })

  const deleteMutation = useMutation(
    (id) => api.delete(`/reports/reports/${id}/`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('reports')
        toast.success('تم حذف التقرير بنجاح')
      },
      onError: () => {
        toast.error('حدث خطأ أثناء حذف التقرير')
      }
    }
  )

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getStatusText = (status) => {
    const texts = {
      pending: 'قيد الانتظار',
      processing: 'جاري التجهيز',
      completed: 'مكتمل',
      failed: 'فشل',
    }
    return texts[status] || status
  }

  if (isLoading) return <LoadingSpinner />

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">التقارير</h1>
        <Link to="/reports/generate" className="btn-primary">
          + إنشاء تقرير جديد
        </Link>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">العنوان</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">النوع</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الصيغة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الحالة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">التاريخ</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {reports?.results?.map((report) => (
                <tr key={report.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link to={`/reports/${report.id}`} className="text-primary-600 hover:underline">
                      {report.title}
                    </Link>
                  </td>
                  <td className="px-6 py-4 text-sm">{report.report_type_display}</td>
                  <td className="px-6 py-4 text-sm">{report.format_display}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(report.status)}`}>
                      {getStatusText(report.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {format(new Date(report.generated_at), 'dd/MM/yyyy', { locale: ar })}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      {report.status === 'completed' && report.file_url && (
                        <a
                          href={report.file_url}
                          download
                          className="text-primary-600 hover:text-primary-800 text-sm"
                        >
                          تحميل
                        </a>
                      )}
                      <button
                        onClick={() => deleteMutation.mutate(report.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        حذف
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Reports