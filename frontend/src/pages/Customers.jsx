import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

const Customers = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    customer_type: 'regular',
    is_active: true,
  })
  
  const queryClient = useQueryClient()

  // جلب العملاء
  const { data: customers, isLoading, error } = useQuery({
    queryKey: ['customers'],
    queryFn: async () => {
      const response = await api.get('/customers/')
      console.log('👤 Customers response:', response.data)
      return response.data
    }
  })

  // إنشاء عميل
  const createMutation = useMutation({
    mutationFn: async (data) => {
      console.log('📤 Sending customer data:', data)
      const response = await api.post('/customers/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['customers'])
      toast.success('✅ تم إضافة العميل بنجاح')
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

  // تحديث عميل
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }) => {
      console.log('📤 Updating customer:', id, data)
      const response = await api.patch(`/customers/${id}/`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['customers'])
      toast.success('✅ تم تحديث العميل بنجاح')
      setIsModalOpen(false)
      resetForm()
    },
    onError: (error) => {
      console.error('❌ Update error:', error.response?.data)
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // حذف عميل
  const deleteMutation = useMutation({
    mutationFn: async (id) => {
      await api.delete(`/customers/${id}/`)
      return id
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['customers'])
      toast.success('✅ تم حذف العميل بنجاح')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  const resetForm = () => {
    setFormData({
      name: '',
      phone: '',
      email: '',
      customer_type: 'regular',
      is_active: true,
    })
    setEditingCustomer(null)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // ✅ تنظيف البيانات قبل الإرسال
    const data = {
      name: formData.name.trim(),
      phone: formData.phone.trim(),
      email: formData.email ? formData.email.trim() : '',
      customer_type: formData.customer_type,
      is_active: formData.is_active,
    }
    
    console.log('📤 Final data to send:', data)
    
    if (editingCustomer) {
      updateMutation.mutate({ id: editingCustomer.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const handleEdit = (customer) => {
    setEditingCustomer(customer)
    setFormData({
      name: customer.name,
      phone: customer.phone,
      email: customer.email || '',
      customer_type: customer.customer_type || 'regular',
      is_active: customer.is_active !== undefined ? customer.is_active : true,
    })
    setIsModalOpen(true)
  }

  const handleDelete = (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذا العميل؟')) {
      deleteMutation.mutate(id)
    }
  }

  if (isLoading) return <LoadingSpinner />
  
  if (error) {
    console.error('❌ Error fetching customers:', error)
    return (
      <div className="text-center py-10 text-red-600">
        <p>حدث خطأ في تحميل العملاء</p>
        <p className="text-sm">{error.message}</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">العملاء</h1>
        <button
          onClick={() => {
            resetForm()
            setIsModalOpen(true)
          }}
          className="btn-primary"
        >
          + إضافة عميل
        </button>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">#</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الاسم</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الهاتف</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">البريد</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">النوع</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الحالة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">تاريخ الإنشاء</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {customers?.results?.map((customer, index) => (
                <tr key={customer.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">{index + 1}</td>
                  <td className="px-6 py-4 font-medium">{customer.name}</td>
                  <td className="px-6 py-4">{customer.display_phone || customer.phone}</td>
                  <td className="px-6 py-4">{customer.email || '-'}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      customer.customer_type === 'vip' ? 'bg-yellow-100 text-yellow-800' :
                      customer.customer_type === 'corporate' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {customer.customer_type === 'vip' && '⭐ VIP'}
                      {customer.customer_type === 'regular' && 'عادي'}
                      {customer.customer_type === 'corporate' && 'شركة'}
                      {customer.customer_type === 'agency' && 'وكالة'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      customer.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {customer.is_active ? 'نشط' : 'غير نشط'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {new Date(customer.created_at).toLocaleDateString('ar-EG')}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(customer)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        تعديل
                      </button>
                      <button
                        onClick={() => handleDelete(customer.id)}
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

      {/* Modal إضافة/تعديل عميل */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">
              {editingCustomer ? 'تعديل عميل' : 'إضافة عميل جديد'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">الاسم</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="label">رقم الهاتف</label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="input"
                  required
                  placeholder="مثال: 0123456789"
                />
              </div>

              <div>
                <label className="label">البريد الإلكتروني</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="input"
                  placeholder="اختياري"
                />
              </div>

              <div>
                <label className="label">نوع العميل</label>
                <select
                  value={formData.customer_type}
                  onChange={(e) => setFormData({ ...formData, customer_type: e.target.value })}
                  className="input"
                >
                  <option value="regular">عادي</option>
                  <option value="vip">VIP ⭐</option>
                  <option value="corporate">شركة / مؤسسة</option>
                  <option value="agency">وكالة / استوديو</option>
                </select>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="w-4 h-4"
                />
                <label className="text-sm">نشط</label>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  disabled={createMutation.isLoading || updateMutation.isLoading}
                  className="btn-primary flex-1 py-3 disabled:opacity-50"
                >
                  {createMutation.isLoading || updateMutation.isLoading
                    ? 'جاري الحفظ...'
                    : editingCustomer ? 'تحديث' : 'إضافة'
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

export default Customers