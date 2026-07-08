import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

const Users = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirm_password: '',
    role: 'receptionist',
    is_active: true,
    is_superuser: false,
  })
  
  const queryClient = useQueryClient()

  // جلب المستخدمين
  const { data: users, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await api.get('/users/')
      return response.data
    }
  })

  // إنشاء مستخدم
  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/users/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['users'])
      toast.success('✅ تم إضافة المستخدم بنجاح')
      setIsModalOpen(false)
      resetForm()
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // تحديث مستخدم
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.patch(`/users/${id}/`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['users'])
      toast.success('✅ تم تحديث المستخدم بنجاح')
      setIsModalOpen(false)
      resetForm()
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // حذف مستخدم
  const deleteMutation = useMutation({
    mutationFn: async (id) => {
      await api.delete(`/users/${id}/`)
      return id
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['users'])
      toast.success('✅ تم حذف المستخدم بنجاح')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  // تفعيل/تعطيل مستخدم
  const toggleActiveMutation = useMutation({
    mutationFn: async ({ id }) => {
      const response = await api.post(`/users/${id}/toggle_active/`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['users'])
      toast.success('✅ تم تغيير حالة المستخدم')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || '❌ حدث خطأ')
    }
  })

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      password: '',
      confirm_password: '',
      role: 'receptionist',
      is_active: true,
      is_superuser: false,
    })
    setEditingUser(null)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (formData.password !== formData.confirm_password) {
      toast.error('كلمة المرور غير متطابقة')
      return
    }

    const data = { ...formData }
    
    // لو مفيش كلمة مرور جديدة (في حالة التعديل)
    if (!data.password) {
      delete data.password
      delete data.confirm_password
    }

    // ✅ لو هو مدير كامل، خليه سوبر يوزر
    if (data.role === 'admin' && data.is_superuser) {
      data.is_superuser = true
      data.is_staff = true
    }

    if (editingUser) {
      updateMutation.mutate({ id: editingUser.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const handleEdit = (user) => {
    setEditingUser(user)
    setFormData({
      username: user.username,
      email: user.email || '',
      password: '',
      confirm_password: '',
      role: user.role,
      is_active: user.is_active,
      is_superuser: user.is_superuser || false,
    })
    setIsModalOpen(true)
  }

  const handleDelete = (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذا المستخدم؟')) {
      deleteMutation.mutate(id)
    }
  }

  const handleToggleActive = (id) => {
    toggleActiveMutation.mutate({ id })
  }

  if (isLoading) return <LoadingSpinner />
  
  if (error) {
    console.error('❌ Error fetching users:', error)
    return (
      <div className="text-center py-10 text-red-600">
        <p>حدث خطأ في تحميل المستخدمين</p>
        <p className="text-sm">{error.message}</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">المستخدمين</h1>
        <button
          onClick={() => {
            resetForm()
            setIsModalOpen(true)
          }}
          className="btn-primary"
        >
          + إضافة مستخدم
        </button>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">#</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">اسم المستخدم</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">البريد</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الدور</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">مدير كامل</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الحالة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">تاريخ الإنشاء</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users?.results?.map((user, index) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">{index + 1}</td>
                  <td className="px-6 py-4 font-medium">{user.username}</td>
                  <td className="px-6 py-4">{user.email || '-'}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      user.role === 'admin' ? 'bg-red-100 text-red-800' :
                      user.role === 'photographer' ? 'bg-green-100 text-green-800' :
                      user.role === 'receptionist' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {user.role_display || user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    {user.is_superuser ? '✅' : '❌'}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleToggleActive(user.id)}
                      className={`px-2 py-1 rounded-full text-xs ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {user.is_active ? 'نشط' : 'غير نشط'}
                    </button>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {new Date(user.created_at).toLocaleDateString('ar-EG')}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(user)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        تعديل
                      </button>
                      <button
                        onClick={() => handleDelete(user.id)}
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

      {/* Modal إضافة/تعديل مستخدم */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">
              {editingUser ? 'تعديل مستخدم' : 'إضافة مستخدم جديد'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">اسم المستخدم</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="label">البريد الإلكتروني</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="input"
                />
              </div>

              <div>
                <label className="label">كلمة المرور</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="input"
                  placeholder={editingUser ? 'اتركه فارغاً للتعديل' : ''}
                />
              </div>

              <div>
                <label className="label">تأكيد كلمة المرور</label>
                <input
                  type="password"
                  value={formData.confirm_password}
                  onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                  className="input"
                  placeholder={editingUser ? 'اتركه فارغاً للتعديل' : ''}
                />
              </div>

              <div>
                <label className="label">الدور</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="input"
                >
                  <option value="admin">👑 مدير</option>
                  <option value="receptionist">📞 موظف استقبال</option>
                  <option value="photographer">📸 مصور</option>
                  <option value="manager">🏢 مدير فرع</option>
                  <option value="accountant">💰 محاسب</option>
                  <option value="assistant">🤝 مساعد</option>
                </select>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.is_superuser}
                  onChange={(e) => setFormData({ ...formData, is_superuser: e.target.checked })}
                  className="w-4 h-4"
                />
                <label className="text-sm font-medium text-gray-700">
                  👑 مدير كامل (صلاحية مطلقة)
                </label>
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
                    : editingUser ? 'تحديث' : 'إضافة'
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

export default Users