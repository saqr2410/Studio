import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import { format } from 'date-fns'
import { ar } from 'date-fns/locale'

const ReportDetail = () => {
  const { id } = useParams()

  const { data: report, isLoading } = useQuery(
    ['report', id],
    async () => {
      const response = await api.get(`/reports/reports/${id}/`)
      return response.data
    },
    { refetchInterval: 3000 } // تحديث كل 3 ثواني
  )

  if (isLoading) return <LoadingSpinner />
  if (!report) return <div>التقرير غير موجود</div>

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{report.title}</h1>
        <Link to="/reports" className="btn-secondary">
          ← العودة للتقارير
        </Link>
      </div>

      <div className="card space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-500">النوع</p>
            <p className="font-medium">{report.report_type_display}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">الصيغة</p>
            <p className="font-medium">{report.format_display}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">الحالة</p>
            <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(report.status)}`}>
              {report.status_display}
            </span>
          </div>
          <div>
            <p className="text-sm text-gray-500">تاريخ الإنشاء</p>
            <p className="font-medium">
              {format(new Date(report.generated_at), 'dd/MM/yyyy HH:mm', { locale: ar })}
            </p>
          </div>
        </div>

        {report.start_date && report.end_date && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">تاريخ البداية</p>
              <p className="font-medium">
                {format(new Date(report.start_date), 'dd/MM/yyyy', { locale: ar })}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">تاريخ النهاية</p>
              <p className="font-medium">
                {format(new Date(report.end_date), 'dd/MM/yyyy', { locale: ar })}
              </p>
            </div>
          </div>
        )}

        {report.summary && Object.keys(report.summary).length > 0 && (
          <div>
            <h3 className="font-semibold mb-2">الملخص</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <pre className="text-sm whitespace-pre-wrap">
                {JSON.stringify(report.summary, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {report.status === 'completed' && report.file_url && (
          <div className="flex gap-4 pt-4">
            <a
              href={report.file_url}
              download
              className="btn-primary flex-1 text-center"
            >
              📥 تحميل التقرير
            </a>
          </div>
        )}

        {report.status === 'processing' && (
          <div className="text-center py-4">
            <div className="animate-pulse text-primary-600">
              ⏳ جاري توليد التقرير...
            </div>
          </div>
        )}

        {report.status === 'failed' && (
          <div className="bg-red-50 text-red-800 p-4 rounded-lg">
            <p className="font-semibold">❌ حدث خطأ</p>
            <p className="text-sm">{report.notes}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ReportDetail