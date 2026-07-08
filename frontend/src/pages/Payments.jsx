import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

const Payments = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingPayment, setEditingPayment] = useState(null)
  const [formData, setFormData] = useState({
    booking: '',
    amount: '',
    payment_type: 'deposit',
    payment_method: 'cash',
    status: 'pending',
  })
  
  const queryClient = useQueryClient()

  // جلب المدفوعات
  const { data: payments, isLoading, error } = useQuery({
    queryKey: ['payments'],
    queryFn: async () => {
      const response = await api.get('/payments/')
      return response.data
    }
  })

  // جلب الحجوزات للاختيار
  const { data: bookings } = useQuery({
    queryKey: ['bookings-select'],
    queryFn: async () => {
      const response = await api.get('/bookings/')
      console.log('📚 Bookings for payment:', response.data)
      return response.data
    }
  })

  // إنشاء دفعة
  const createMutation = useMutation({
    mutationFn: async (data) => {
      console.log('📤 Sending payment data:', data)
      const response = await api.post('/payments/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['payments'])
      queryClient.invalidateQueries(['finance-summary'])
      queryClient.invalidateQueries(['finance-monthly'])
      toast.success('✅ تم إضافة الدفعة بنجاح')
      setIsModalOpen(false)
      resetForm()
    },
    onError: (error) => {
      console.error('❌ Full error:', error.response?.data)
      const errorData = error.response?.data
      
      if (typeof errorData === 'object') {
        const messages = Object.entries(errorData)
          .map(([field, msg]) => {
            if (Array.isArray(msg)) {
              return `${field}: ${msg.join(', ')}`
            }
            return `${field}: ${msg}`
          })
          .join('\n')
        toast.error(messages || '❌ حدث خطأ')
      } else {
        toast.error(errorData?.detail || '❌ حدث خطأ')
      }
    }
  })

  // تحديث دفعة
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/payments/${id}/`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['payments'])
      queryClient.invalidateQueries(['finance-summary'])
      queryClient.invalidateQueries(['finance-monthly'])
      toast.success('✅ تم تحديث الدفعة بنجاح')
      setIsModalOpen(false)
      resetForm()
    },
    onError: (error) => {
      console.error('❌ Update error:', error.response?.data)
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // حذف دفعة
  const deleteMutation = useMutation({
    mutationFn: async (id) => {
      await api.delete(`/payments/${id}/`)
      return id
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['payments'])
      queryClient.invalidateQueries(['finance-summary'])
      queryClient.invalidateQueries(['finance-monthly'])
      toast.success('✅ تم حذف الدفعة بنجاح')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // تأكيد دفعة
  const confirmMutation = useMutation({
    mutationFn: async (id) => {
      const response = await api.post(`/payments/${id}/confirm/`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['payments'])
      queryClient.invalidateQueries(['finance-summary'])
      queryClient.invalidateQueries(['finance-monthly'])
      toast.success('✅ تم تأكيد الدفعة بنجاح')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  const resetForm = () => {
    setFormData({
      booking: '',
      amount: '',
      payment_type: 'deposit',
      payment_method: 'cash',
      status: 'pending',
    })
    setEditingPayment(null)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const bookingId = parseInt(formData.booking)
    if (!bookingId || isNaN(bookingId)) {
      toast.error('❌ يرجى اختيار حجز صحيح')
      return
    }
    
    const data = {
      booking: bookingId,
      amount: parseFloat(formData.amount),
      payment_type: formData.payment_type,
      payment_method: formData.payment_method,
      status: formData.status || 'pending',
    }
    
    console.log('📤 Final data to send:', data)
    
    if (editingPayment) {
      updateMutation.mutate({ id: editingPayment.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const handleEdit = (payment) => {
    setEditingPayment(payment)
    setFormData({
      booking: payment.booking || '',
      amount: payment.amount || '',
      payment_type: payment.payment_type || 'deposit',
      payment_method: payment.payment_method || 'cash',
      status: payment.status || 'pending',
    })
    setIsModalOpen(true)
  }

  const handleDelete = (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذه الدفعة؟')) {
      deleteMutation.mutate(id)
    }
  }

  const handleConfirm = (id) => {
    if (window.confirm('هل أنت متأكد من تأكيد هذه الدفعة؟')) {
      confirmMutation.mutate(id)
    }
  }

  if (isLoading) return <LoadingSpinner />
  
  if (error) {
    console.error('❌ Error fetching payments:', error)
    return (
      <div className="text-center py-10 text-red-600">
        <p>حدث خطأ في تحميل المدفوعات</p>
        <p className="text-sm">{error.message}</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">المدفوعات</h1>
        <button
          onClick={() => {
            resetForm()
            setIsModalOpen(true)
          }}
          className="btn-primary"
        >
          + إضافة دفعة
        </button>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">#</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الحجز</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">العميل</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">المبلغ</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">نوع الدفعة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">طريقة الدفع</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الحالة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">التاريخ</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {payments?.results?.map((payment, index) => (
                <tr key={payment.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">{index + 1}</td>
                  <td className="px-6 py-4">#{payment.booking}</td>
                  <td className="px-6 py-4">{payment.customer_name || '-'}</td>
                  <td className="px-6 py-4 font-medium">{payment.amount} ج.م</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      payment.payment_type === 'deposit' ? 'bg-blue-100 text-blue-800' :
                      payment.payment_type === 'full' ? 'bg-green-100 text-green-800' :
                      payment.payment_type === 'installment' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {payment.payment_type_display || payment.payment_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {payment.payment_method_display || payment.payment_method}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      payment.status === 'paid' ? 'bg-green-100 text-green-800' :
                      payment.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      payment.status === 'failed' ? 'bg-red-100 text-red-800' :
                      payment.status === 'refunded' ? 'bg-gray-100 text-gray-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {payment.status_display || payment.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {new Date(payment.created_at).toLocaleDateString('ar-EG')}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {payment.status === 'pending' && (
                        <button
                          onClick={() => handleConfirm(payment.id)}
                          className="text-green-600 hover:text-green-800 text-xs"
                        >
                          تأكيد
                        </button>
                      )}
                      <button
                        onClick={() => handleEdit(payment)}
                        className="text-blue-600 hover:text-blue-800 text-xs"
                      >
                        تعديل
                      </button>
                      <button
                        onClick={() => handleDelete(payment.id)}
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

      {/* Modal إضافة/تعديل دفعة */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">
              {editingPayment ? 'تعديل دفعة' : 'إضافة دفعة جديدة'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">الحجز</label>
                <select
                  value={formData.booking}
                  onChange={(e) => setFormData({ ...formData, booking: e.target.value })}
                  className="input"
                  required
                >
                  <option value="">اختر حجز</option>
                  {bookings?.results?.map((booking) => (
                    <option key={booking.id} value={booking.id}>
                      #{booking.id} - {booking.customer_name} ({booking.date}) - {booking.price} ج.م
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">المبلغ</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="input"
                  required
                  placeholder="0.00"
                />
              </div>

              <div>
                <label className="label">نوع الدفعة</label>
                <select
                  value={formData.payment_type}
                  onChange={(e) => setFormData({ ...formData, payment_type: e.target.value })}
                  className="input"
                >
                  <option value="deposit">دفعة مقدمة</option>
                  <option value="installment">قسط</option>
                  <option value="full">دفعة كاملة</option>
                  <option value="extra">دفعة إضافية</option>
                  <option value="remaining">المتبقي</option>
                </select>
              </div>

              <div>
                <label className="label">طريقة الدفع</label>
                <select
                  value={formData.payment_method}
                  onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                  className="input"
                >
                  <option value="cash">نقدي</option>
                  <option value="bank_transfer">تحويل بنكي</option>
                  <option value="credit_card">بطاقة ائتمان</option>
                  <option value="debit_card">بطاقة خصم</option>
                  <option value="cheque">شيك</option>
                  <option value="mobile">محفظة إلكترونية</option>
                  <option value="online">دفع إلكتروني</option>
                </select>
              </div>

              <div>
                <label className="label">الحالة</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="input"
                >
                  <option value="pending">قيد الانتظار</option>
                  <option value="paid">مدفوع</option>
                  <option value="failed">فشل</option>
                  <option value="refunded">مسترد</option>
                </select>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  disabled={createMutation.isLoading || updateMutation.isLoading}
                  className="btn-primary flex-1 py-3 disabled:opacity-50"
                >
                  {createMutation.isLoading || updateMutation.isLoading
                    ? 'جاري الحفظ...'
                    : editingPayment ? 'تحديث' : 'إضافة'
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

export default Payments