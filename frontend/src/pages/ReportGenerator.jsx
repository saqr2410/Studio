import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'  // ✅ هذا السطر بس
import api from '../api/axios'
import toast from 'react-hot-toast'

const ReportGenerator = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    title: '',
    report_type: 'booking',
    format: 'pdf',
    start_date: '',
    end_date: '',
    filters: {},
  })

  const generateMutation = useMutation(
    (data) => api.post('/reports/reports/', data),
    {
      onSuccess: (response) => {
        toast.success('تم بدء توليد التقرير 🚀')
        navigate(`/reports/${response.data.id}`)
      },
      onError: () => {
        toast.error('حدث خطأ أثناء توليد التقرير')
      }
    }
  )

  const handleSubmit = (e) => {
    e.preventDefault()
    generateMutation.mutate(formData)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">إنشاء تقرير جديد</h1>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label className="label">عنوان التقرير</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="input"
            placeholder="أدخل عنوان التقرير"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label">نوع التقرير</label>
            <select
              name="report_type"
              value={formData.report_type}
              onChange={handleChange}
              className="input"
            >
              <option value="booking">حجوزات</option>
              <option value="financial">مالي</option>
              <option value="customer">عملاء</option>
              <option value="payment">مدفوعات</option>
              <option value="expense">مصروفات</option>
              <option value="profit">أرباح</option>
              <option value="daily">يومي</option>
              <option value="weekly">أسبوعي</option>
              <option value="monthly">شهري</option>
              <option value="yearly">سنوي</option>
            </select>
          </div>

          <div>
            <label className="label">صيغة التقرير</label>
            <select
              name="format"
              value={formData.format}
              onChange={handleChange}
              className="input"
            >
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label">تاريخ البداية</label>
            <input
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleChange}
              className="input"
            />
          </div>
          <div>
            <label className="label">تاريخ النهاية</label>
            <input
              type="date"
              name="end_date"
              value={formData.end_date}
              onChange={handleChange}
              className="input"
            />
          </div>
        </div>

        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={generateMutation.isLoading}
            className="btn-primary flex-1 py-3 disabled:opacity-50"
          >
            {generateMutation.isLoading ? 'جاري التوليد...' : 'توليد التقرير'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/reports')}
            className="btn-secondary px-6"
          >
            إلغاء
          </button>
        </div>
      </form>
    </div>
  )
}

export default ReportGenerator