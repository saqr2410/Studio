from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth.models import AnonymousUser


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 BASE ROLE PERMISSION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BaseRolePermission(BasePermission):
    """
    كلاس أساسي للصلاحيات حسب الدور
    """
    allowed_roles = []
    allowed_methods = []
    denied_methods = []

    def has_permission(self, request, view):
        user = request.user
        
        # التحقق من المصادقة
        if not user or not user.is_authenticated:
            return False
        
        # التحقق من وجود دور
        if not hasattr(user, 'role'):
            return False
        
        # ✅ لو الدور admin، سمح بكل حاجة
        if user.role == 'admin':
            return True
        
        # التحقق من حالة المستخدم
        if hasattr(user, 'is_active') and not user.is_active:
            return False
        
        # التحقق من أن المستخدم ليس محظوراً (إذا كان لديك حقل)
        if hasattr(user, 'is_blacklisted') and user.is_blacklisted:
            return False
        
        # التحقق من الأدوار المسموحة
        if self.allowed_roles and user.role not in self.allowed_roles:
            return False
        
        # التحقق من الطرق المسموحة/الممنوعة
        if self.allowed_methods and request.method not in self.allowed_methods:
            return False
        
        if self.denied_methods and request.method in self.denied_methods:
            return False
        
        return True

    def has_object_permission(self, request, view, obj):
        """
        صلاحية على مستوى الكائن (اختياري)
        يمكن تخصيصها في الكلاسات الفرعية
        """
        user = request.user
        
        # ✅ لو الدور admin، سمح بكل حاجة على مستوى الكائن
        if user.role == 'admin':
            return True
        
        return True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 ROLE-BASED PERMISSIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class IsAdmin(BaseRolePermission):
    """فقط المدير"""
    allowed_roles = ['admin']


class IsManager(BaseRolePermission):
    """فقط مدير الفرع"""
    allowed_roles = ['manager']


class IsReceptionist(BaseRolePermission):
    """فقط موظف الاستقبال"""
    allowed_roles = ['receptionist']


class IsPhotographer(BaseRolePermission):
    """فقط المصور"""
    allowed_roles = ['photographer']


class IsAccountant(BaseRolePermission):
    """فقط المحاسب"""
    allowed_roles = ['accountant']


class IsAssistant(BaseRolePermission):
    """فقط المساعد"""
    allowed_roles = ['assistant']


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 COMBINED PERMISSIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class IsAdminOrManager(BaseRolePermission):
    """مدير أو مدير فرع"""
    allowed_roles = ['admin', 'manager']


class IsAdminOrReceptionist(BaseRolePermission):
    """مدير أو موظف استقبال"""
    allowed_roles = ['admin', 'receptionist']


class IsAdminOrPhotographer(BaseRolePermission):
    """مدير أو مصور"""
    allowed_roles = ['admin', 'photographer']


class IsAdminOrAccountant(BaseRolePermission):
    """مدير أو محاسب"""
    allowed_roles = ['admin', 'accountant']


class IsReceptionistOrAdmin(BaseRolePermission):
    """موظف استقبال أو مدير"""
    allowed_roles = ['admin', 'receptionist']


class IsPhotographerOrAdmin(BaseRolePermission):
    """مصور أو مدير"""
    allowed_roles = ['admin', 'photographer']


class IsStaff(BaseRolePermission):
    """جميع الموظفين (كل الأدوار ما عدا admin)"""
    allowed_roles = ['receptionist', 'photographer', 'manager', 'accountant', 'assistant']


class IsAnyRole(BaseRolePermission):
    """أي دور (جميع المستخدمين المصادقين)"""
    allowed_roles = ['admin', 'receptionist', 'photographer', 'manager', 'accountant', 'assistant']


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 PERMISSION BY METHOD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class IsAdminOrReadOnly(BaseRolePermission):
    """
    مدير يمكنه كل شيء، الآخرون قراءة فقط
    """
    allowed_roles = ['admin', 'receptionist', 'photographer', 'manager', 'accountant', 'assistant']
    
    def has_permission(self, request, view):
        # السماح للمدير بكل شيء
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # السماح للآخرين بالقراءة فقط
        if request.method in SAFE_METHODS:
            return super().has_permission(request, view)
        
        return False


class IsOwnerOrAdmin(BaseRolePermission):
    """
    المدير أو مالك الكائن فقط
    """
    allowed_roles = ['admin']
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # المدير يملك صلاحية كاملة
        if user.role == 'admin':
            return True
        
        # التحقق من أن المستخدم هو مالك الكائن
        # يجب تخصيص هذا حسب الموديل
        if hasattr(obj, 'created_by') and obj.created_by == user:
            return True
        if hasattr(obj, 'user') and obj.user == user:
            return True
        if hasattr(obj, 'photographer') and obj.photographer == user:
            return True
        
        return False


class IsReceptionistOrAdminCreateOnly(BaseRolePermission):
    """
    موظف الاستقبال يمكنه إنشاء فقط، المدير كل شيء
    """
    allowed_roles = ['admin', 'receptionist']
    
    def has_permission(self, request, view):
        user = request.user
        
        # المدير يمكنه كل شيء
        if user.role == 'admin':
            return True
        
        # موظف الاستقبال يمكنه فقط POST (إنشاء)
        if user.role == 'receptionist' and request.method == 'POST':
            return True
        
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 CUSTOM PERMISSIONS FOR SPECIFIC ACTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CanManageUsers(BaseRolePermission):
    """يمكنه إدارة المستخدمين"""
    allowed_roles = ['admin', 'manager']


class CanManageBookings(BaseRolePermission):
    """يمكنه إدارة الحجوزات"""
    allowed_roles = ['admin', 'receptionist', 'manager']


class CanManagePayments(BaseRolePermission):
    """يمكنه إدارة المدفوعات"""
    allowed_roles = ['admin', 'accountant', 'manager']


class CanViewFinancials(BaseRolePermission):
    """يمكنه عرض التقارير المالية"""
    allowed_roles = ['admin', 'accountant', 'manager']


class CanManageExpenses(BaseRolePermission):
    """يمكنه إدارة المصروفات"""
    allowed_roles = ['admin', 'accountant', 'manager']


class CanManageCustomers(BaseRolePermission):
    """يمكنه إدارة العملاء"""
    allowed_roles = ['admin', 'receptionist', 'manager']


class CanViewReports(BaseRolePermission):
    """يمكنه عرض التقارير"""
    allowed_roles = ['admin', 'manager', 'accountant']


class CanDeleteRecords(BaseRolePermission):
    """يمكنه حذف السجلات"""
    allowed_roles = ['admin']  # فقط المدير يمكنه الحذف


class CanExportData(BaseRolePermission):
    """يمكنه تصدير البيانات"""
    allowed_roles = ['admin', 'manager', 'accountant']


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 PERMISSION FOR SPECIFIC MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class IsBookingOwnerOrAdmin(BaseRolePermission):
    """
    مصور الحجز أو المدير
    """
    allowed_roles = ['admin']
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # المدير يمكنه كل شيء
        if user.role == 'admin':
            return True
        
        # المصور يمكنه الوصول لحجوزاته فقط
        if user.role == 'photographer' and hasattr(obj, 'photographer'):
            return obj.photographer == user
        
        return False


class IsCustomerOwnerOrAdmin(BaseRolePermission):
    """
    عميل الحجز أو المدير
    """
    allowed_roles = ['admin']
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.role == 'admin':
            return True
        
        if hasattr(obj, 'customer') and obj.customer:
            return obj.customer == user
        
        return False


class IsAssignedPhotographer(BaseRolePermission):
    """
    المصور المعين فقط
    """
    allowed_roles = ['admin', 'photographer']
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.role == 'admin':
            return True
        
        if user.role == 'photographer' and hasattr(obj, 'photographer'):
            return obj.photographer == user
        
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 PERMISSION CLASSES FOR USER SPECIFIC ACTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CanViewProfile(BaseRolePermission):
    """يمكنه عرض الملف الشخصي"""
    allowed_roles = ['admin', 'receptionist', 'photographer', 'manager', 'accountant', 'assistant']
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # يمكنه عرض ملفه الشخصي فقط
        if obj == user:
            return True
        
        # المدير يمكنه عرض كل الملفات
        if user.role == 'admin':
            return True
        
        return False


class CanEditProfile(BaseRolePermission):
    """يمكنه تعديل الملف الشخصي"""
    allowed_roles = ['admin']
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # يمكنه تعديل ملفه الشخصي فقط
        if obj == user and request.method in ['PUT', 'PATCH']:
            return True
        
        # المدير يمكنه تعديل كل الملفات
        if user.role == 'admin':
            return True
        
        return False


class CanChangePassword(BaseRolePermission):
    """يمكنه تغيير كلمة المرور"""
    allowed_roles = ['admin', 'receptionist', 'photographer', 'manager', 'accountant', 'assistant']
    
    def has_object_permission(self, request, view, obj):
        # يمكنه تغيير كلمة المرور الخاصة به فقط
        return obj == request.user


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 PERMISSION FOR FINANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CanViewIncome(BaseRolePermission):
    """يمكنه عرض الإيرادات"""
    allowed_roles = ['admin', 'accountant', 'manager']


class CanManageIncome(BaseRolePermission):
    """يمكنه إدارة الإيرادات"""
    allowed_roles = ['admin', 'accountant']


class CanViewExpenses(BaseRolePermission):
    """يمكنه عرض المصروفات"""
    allowed_roles = ['admin', 'accountant', 'manager']


class CanManageExpenses(BaseRolePermission):
    """يمكنه إدارة المصروفات"""
    allowed_roles = ['admin', 'accountant']


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 DYNAMIC PERMISSION (للحالات المعقدة)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DynamicPermission(BasePermission):
    """
    صلاحية ديناميكية يمكن تخصيصها عند الاستخدام
    """
    
    def __init__(self, allowed_roles=None, allowed_methods=None, check_owner=False, owner_field='created_by'):
        self.allowed_roles = allowed_roles or []
        self.allowed_methods = allowed_methods or []
        self.check_owner = check_owner
        self.owner_field = owner_field
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        if self.allowed_roles and user.role not in self.allowed_roles:
            return False
        
        if self.allowed_methods and request.method not in self.allowed_methods:
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        if not self.check_owner:
            return True
        
        user = request.user
        
        # المدير يمكنه كل شيء
        if user.role == 'admin':
            return True
        
        # التحقق من مالك الكائن
        if hasattr(obj, self.owner_field):
            owner = getattr(obj, self.owner_field)
            return owner == user
        
        return False