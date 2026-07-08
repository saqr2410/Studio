import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

const Bookings = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingBooking, setEditingBooking] = useState(null)
  const [formData, setFormData] = useState({
    customer: '',
    photographer: '',
    date: '',
    start_time: '',
    end_time: '',
    status: 'pending',
    price: '',
    title: '',
    location: '',
    notes: '',
  })
  
  const queryClient = useQueryClient()

  // جلب الحجوزات
  const { data: bookings, isLoading, error } = useQuery({
    queryKey: ['bookings'],
    queryFn: async () => {
      const response = await api.get('/bookings/')
      console.log('📅 Bookings response:', response.data)
      return response.data
    }
  })

  // جلب العملاء للاختيار
  const { data: customers } = useQuery({
    queryKey: ['customers-select'],
    queryFn: async () => {
      const response = await api.get('/customers/')
      console.log('👤 Customers response:', response.data)
      return response.data
    }
  })

  // جلب المصورين للاختيار
  const { data: photographers } = useQuery({
    queryKey: ['photographers-select'],
    queryFn: async () => {
      const response = await api.get('/users/photographers/')
      console.log('📸 Photographers response:', response.data)
      return response.data
    }
  })

  // إنشاء حجز
  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/bookings/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['bookings'])
      toast.success('✅ تم إضافة الحجز بنجاح')
      setIsModalOpen(false)
      resetForm()
    },
    onError: (error) => {
      console.error('❌ Create error:', error.response?.data)
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // تحديث حجز
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/bookings/${id}/`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['bookings'])
      toast.success('✅ تم تحديث الحجز بنجاح')
      setIsModalOpen(false)
      resetForm()
    },
    onError: (error) => {
      console.error('❌ Update error:', error.response?.data)
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // حذف حجز
  const deleteMutation = useMutation({
    mutationFn: async (id) => {
      await api.delete(`/bookings/${id}/`)
      return id
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['bookings'])
      toast.success('✅ تم حذف الحجز بنجاح')
    },
    onError: (error) => {
      console.error('❌ Delete error:', error.response?.data)
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // تأكيد حجز
  const confirmMutation = useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/bookings/${id}/confirm/`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['bookings'])
      toast.success('✅ تم تأكيد الحجز بنجاح')
    },
    onError: (error) => {
      console.error('❌ Confirm error:', error.response?.data)
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // إلغاء حجز
  const cancelMutation = useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/bookings/${id}/cancel/`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['bookings'])
      toast.success('✅ تم إلغاء الحجز بنجاح')
    },
    onError: (error) => {
      console.error('❌ Cancel error:', error.response?.data)
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // إنهاء حجز
  const completeMutation = useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/bookings/${id}/complete/`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['bookings'])
      toast.success('✅ تم إنهاء الحجز بنجاح')
    },
    onError: (error) => {
      console.error('❌ Complete error:', error.response?.data)
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  const resetForm = () => {
    setFormData({
      customer: '',
      photographer: '',
      date: '',
      start_time: '',
      end_time: '',
      status: 'pending',
      price: '',
      title: '',
      location: '',
      notes: '',
    })
    setEditingBooking(null)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const data = {
      ...formData,
      price: parseFloat(formData.price) || 0,
    }
    
    if (editingBooking) {
      updateMutation.mutate({ id: editingBooking.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const handleEdit = (booking) => {
    setEditingBooking(booking)
    setFormData({
      customer: booking.customer || '',
      photographer: booking.photographer || '',
      date: booking.date || '',
      start_time: booking.start_time || '',
      end_time: booking.end_time || '',
      status: booking.status || 'pending',
      price: booking.price || '',
      title: booking.title || '',
      location: booking.location || '',
      notes: booking.notes || '',
    })
    setIsModalOpen(true)
  }

  const handleDelete = (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذا الحجز؟')) {
      deleteMutation.mutate(id)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-purple-100 text-purple-800',
      done: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
      no_show: 'bg-gray-100 text-gray-800',
    }
    return badges[status] || 'bg-gray-100 text-gray-800'
  }

  const getStatusText = (status) => {
    const texts = {
      pending: 'قيد الانتظار',
      confirmed: 'مؤكد',
      in_progress: 'قيد التنفيذ',
      done: 'منتهي',
      cancelled: 'ملغي',
      no_show: 'لم يحضر',
    }
    return texts[status] || status
  }

  if (isLoading) return <LoadingSpinner />
  
  if (error) {
    console.error('❌ Error fetching bookings:', error)
    return (
      <div className="text-center py-10 text-red-600">
        <p>حدث خطأ في تحميل الحجوزات</p>
        <p className="text-sm">{error.message}</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">الحجوزات</h1>
        <button
          onClick={() => {
            resetForm()
            setIsModalOpen(true)
          }}
          className="btn-primary"
        >
          + إضافة حجز
        </button>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">#</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">العميل</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">المصور</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">التاريخ</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الوقت</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">السعر</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الحالة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {bookings?.results?.map((booking, index) => (
                <tr key={booking.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">{index + 1}</td>
                  <td className="px-6 py-4 font-medium">{booking.customer_name}</td>
                  <td className="px-6 py-4">{booking.photographer_name}</td>
                  <td className="px-6 py-4">
                    {new Date(booking.date).toLocaleDateString('ar-EG')}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {booking.start_time} - {booking.end_time}
                  </td>
                  <td className="px-6 py-4">{booking.price} ج.م</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(booking.status)}`}>
                      {getStatusText(booking.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {booking.status === 'pending' && (
                        <>
                          <button
                            onClick={() => confirmMutation.mutate(booking.id)}
                            className="text-green-600 hover:text-green-800 text-xs"
                          >
                            تأكيد
                          </button>
                          <button
                            onClick={() => cancelMutation.mutate(booking.id)}
                            className="text-red-600 hover:text-red-800 text-xs"
                          >
                            إلغاء
                          </button>
                        </>
                      )}
                      {booking.status === 'confirmed' && (
                        <>
                          <button
                            onClick={() => completeMutation.mutate(booking.id)}
                            className="text-blue-600 hover:text-blue-800 text-xs"
                          >
                            إنهاء
                          </button>
                          <button
                            onClick={() => cancelMutation.mutate(booking.id)}
                            className="text-red-600 hover:text-red-800 text-xs"
                          >
                            إلغاء
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => handleEdit(booking)}
                        className="text-blue-600 hover:text-blue-800 text-xs"
                      >
                        تعديل
                      </button>
                      <button
                        onClick={() => handleDelete(booking.id)}
                        className="text-red-600 hover:text-red-800 text-xs"
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

      {/* Modal إضافة/تعديل حجز */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">
              {editingBooking ? 'تعديل حجز' : 'إضافة حجز جديد'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">العميل</label>
                  <select
                    value={formData.customer}
                    onChange={(e) => setFormData({ ...formData, customer: e.target.value })}
                    className="input"
                    required
                  >
                    <option value="">اختر عميل</option>
                    {customers?.results?.map((customer) => (
                      <option key={customer.id} value={customer.id}>
                        {customer.name} - {customer.phone}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="label">المصور</label>
                  <select
                    value={formData.photographer}
                    onChange={(e) => setFormData({ ...formData, photographer: e.target.value })}
                    className="input"
                    required
                  >
                    <option value="">اختر مصور</option>
                    {photographers?.map((photographer) => (
                      <option key={photographer.id} value={photographer.id}>
                        {photographer.full_name || photographer.username}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="label">التاريخ</label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    className="input"
                    required
                  />
                </div>

                <div>
                  <label className="label">وقت البداية</label>
                  <input
                    type="time"
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                    className="input"
                    required
                  />
                </div>

                <div>
                  <label className="label">وقت النهاية</label>
                  <input
                    type="time"
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    className="input"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">السعر</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    className="input"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="label">الحالة</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="input"
                  >
                    <option value="pending">قيد الانتظار</option>
                    <option value="confirmed">مؤكد</option>
                    <option value="in_progress">قيد التنفيذ</option>
                    <option value="done">منتهي</option>
                    <option value="cancelled">ملغي</option>
                    <option value="no_show">لم يحضر</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="label">العنوان</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="input"
                  placeholder="عنوان الحجز (اختياري)"
                />
              </div>

              <div>
                <label className="label">الموقع</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="input"
                  placeholder="موقع التصوير (اختياري)"
                />
              </div>

              <div>
                <label className="label">ملاحظات</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="input"
                  rows="3"
                  placeholder="ملاحظات إضافية (اختياري)"
                />
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  disabled={createMutation.isLoading || updateMutation.isLoading}
                  className="btn-primary flex-1 py-3 disabled:opacity-50"
                >
                  {createMutation.isLoading || updateMutation.isLoading
                    ? 'جاري الحفظ...'
                    : editingBooking ? 'تحديث' : 'إضافة'
                  }
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsModalOpen(false)
                    resetForm()
                  }}
                  className="btn-secondary px-6"
                >
                  إلغاء
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Bookings