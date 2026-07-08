from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class User(AbstractUser):
    """
    نموذج المستخدم الاحترافي
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 ROLES CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'مدير'
        RECEPTIONIST = 'receptionist', 'موظف استقبال'
        PHOTOGRAPHER = 'photographer', 'مصور'
        MANAGER = 'manager', 'مدير فرع'
        ACCOUNTANT = 'accountant', 'محاسب'
        ASSISTANT = 'assistant', 'مساعد'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 GENDER CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Gender(models.TextChoices):
        MALE = 'male', 'ذكر'
        FEMALE = 'female', 'أنثى'
        OTHER = 'other', 'آخر'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 STATUS CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'نشط'
        INACTIVE = 'inactive', 'غير نشط'
        SUSPENDED = 'suspended', 'موقوف'
        ON_LEAVE = 'on_leave', 'في إجازة'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Fields
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # ── الحقول الأساسية ──
    role = models.CharField(
        'الدور',
        max_length=20,
        choices=Roles.choices,
        default=Roles.RECEPTIONIST,
        db_index=True
    )
    
    email = models.EmailField(
        'البريد الإلكتروني',
        unique=True,
        db_index=True
    )
    
    phone = models.CharField(
        'رقم الهاتف',
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{10,15}$',
                message='رقم الهاتف يجب أن يكون صحيحاً'
            )
        ],
        help_text='مثال: +201234567890'
    )
    
    # ── معلومات شخصية ──
    gender = models.CharField(
        'الجنس',
        max_length=10,
        choices=Gender.choices,
        blank=True,
        null=True
    )
    
    date_of_birth = models.DateField(
        'تاريخ الميلاد',
        blank=True,
        null=True
    )
    
    profile_picture = models.ImageField(
        'الصورة الشخصية',
        upload_to='profiles/%Y/%m/',
        blank=True,
        null=True
    )
    
    bio = models.TextField(
        'السيرة الذاتية',
        blank=True,
        help_text='نبذة عن المستخدم'
    )
    
    # ── العنوان ──
    address = models.TextField(
        'العنوان',
        blank=True
    )
    
    city = models.CharField(
        'المدينة',
        max_length=100,
        blank=True
    )
    
    country = models.CharField(
        'الدولة',
        max_length=100,
        default='مصر',
        blank=True
    )
    
    # ── حالة المستخدم ──
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )
    
    is_verified = models.BooleanField(
        'تم التحقق',
        default=False,
        help_text='تأكيد البريد الإلكتروني أو الهاتف'
    )
    
    # ── التواريخ الإضافية ──
    last_active = models.DateTimeField(
        'آخر نشاط',
        blank=True,
        null=True
    )
    
    hire_date = models.DateField(
        'تاريخ التوظيف',
        blank=True,
        null=True,
        help_text='تاريخ بداية العمل'
    )
    
    # ── المهارات والتخصصات ──
    skills = models.JSONField(
        'المهارات',
        default=list,
        blank=True,
        help_text='قائمة المهارات (مثال: ["تصوير", "تعديل صور", "فيديو"])'
    )
    
    specialties = models.JSONField(
        'التخصصات',
        default=list,
        blank=True,
        help_text='تخصصات التصوير (مثال: ["زفاف", "أطفال", "موديل"])'
    )
    
    # ── إعدادات الإشعارات ──
    notification_preferences = models.JSONField(
        'تفضيلات الإشعارات',
        default=dict,
        blank=True,
        help_text='إعدادات الإشعارات لكل نوع'
    )
    
    # ── إعدادات التطبيق ──
    theme_preference = models.CharField(
        'تفضيل السمة',
        max_length=20,
        default='light',
        choices=[
            ('light', 'فاتح'),
            ('dark', 'داكن'),
            ('system', 'نظام'),
        ]
    )
    
    language = models.CharField(
        'اللغة',
        max_length=10,
        default='ar',
        choices=[
            ('ar', 'العربية'),
            ('en', 'English'),
        ]
    )
    
    timezone = models.CharField(
        'المنطقة الزمنية',
        max_length=50,
        default='Africa/Cairo'
    )
    
    # ── التواريخ الإدارية ──
    created_at = models.DateTimeField(
        'تاريخ الإنشاء',
        auto_now_add=True,
        db_index=True
    )
    
    updated_at = models.DateTimeField(
        'آخر تحديث',
        auto_now=True
    )
    
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name='تم الإنشاء بواسطة'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Meta
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'
        indexes = [
            models.Index(fields=['role', 'status']),
            models.Index(fields=['email', 'phone']),
            models.Index(fields=['is_active', 'role']),
        ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 String
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Properties
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @property
    def full_name(self):
        """الاسم الكامل"""
        return self.get_full_name() or self.username
    
    @property
    def is_admin(self):
        """هل المستخدم مدير"""
        return self.role == self.Roles.ADMIN
    
    @property
    def is_receptionist(self):
        """هل المستخدم موظف استقبال"""
        return self.role == self.Roles.RECEPTIONIST
    
    @property
    def is_photographer(self):
        """هل المستخدم مصور"""
        return self.role == self.Roles.PHOTOGRAPHER
    
    @property
    def is_manager(self):
        """هل المستخدم مدير فرع"""
        return self.role == self.Roles.MANAGER
    
    @property
    def is_accountant(self):
        """هل المستخدم محاسب"""
        return self.role == self.Roles.ACCOUNTANT
    
    @property
    def is_active_user(self):
        """هل المستخدم نشط"""
        return self.is_active and self.status == self.Status.ACTIVE
    
    @property
    def is_suspended(self):
        """هل المستخدم موقوف"""
        return self.status == self.Status.SUSPENDED
    
    @property
    def is_on_leave(self):
        """هل المستخدم في إجازة"""
        return self.status == self.Status.ON_LEAVE
    
    @property
    def age(self):
        """حساب العمر"""
        if self.date_of_birth:
            today = timezone.now().date()
            age = today.year - self.date_of_birth.year
            if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
                age -= 1
            return age
        return None
    
    @property
    def role_display_ar(self):
        """عرض الدور بالعربية"""
        return dict(self.Roles.choices).get(self.role, self.role)
    
    @property
    def status_display_ar(self):
        """عرض الحالة بالعربية"""
        return dict(self.Status.choices).get(self.status, self.status)
    
    @property
    def gender_display_ar(self):
        """عرض الجنس بالعربية"""
        return dict(self.Gender.choices).get(self.gender, self.gender)
    
    @property
    def dashboard_redirect(self):
        """مسار لوحة التحكم حسب الدور"""
        redirects = {
            self.Roles.ADMIN: '/admin-dashboard',
            self.Roles.MANAGER: '/manager-dashboard',
            self.Roles.RECEPTIONIST: '/reception-dashboard',
            self.Roles.PHOTOGRAPHER: '/photographer-dashboard',
            self.Roles.ACCOUNTANT: '/accountant-dashboard',
            self.Roles.ASSISTANT: '/assistant-dashboard',
        }
        return redirects.get(self.role, '/')
    
    @property
    def permissions_list(self):
        """قائمة الصلاحيات حسب الدور"""
        permissions = {
            self.Roles.ADMIN: ['all'],
            self.Roles.MANAGER: ['view_all', 'manage_staff', 'manage_bookings'],
            self.Roles.RECEPTIONIST: ['view_bookings', 'create_bookings', 'manage_customers'],
            self.Roles.PHOTOGRAPHER: ['view_assigned_bookings', 'update_booking_status'],
            self.Roles.ACCOUNTANT: ['view_financials', 'manage_payments'],
            self.Roles.ASSISTANT: ['view_customers', 'view_bookings'],
        }
        return permissions.get(self.role, [])
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_dashboard_url(self):
        """الحصول على رابط لوحة التحكم"""
        return self.dashboard_redirect
    
    def has_permission(self, permission):
        """التحقق من وجود صلاحية معينة"""
        if self.is_admin:
            return True
        return permission in self.permissions_list
    
    def get_bookings_count(self):
        """عدد الحجوزات للمصور"""
        if self.is_photographer:
            from bookings.models import Booking
            return Booking.objects.filter(photographer=self).count()
        return 0
    
    def get_todays_bookings(self):
        """حجوزات اليوم للمصور"""
        if self.is_photographer:
            from bookings.models import Booking
            from django.utils import timezone
            return Booking.objects.filter(
                photographer=self,
                date=timezone.now().date()
            )
        return None
    
    def get_upcoming_bookings(self):
        """الحجوزات القادمة للمصور"""
        if self.is_photographer:
            from bookings.models import Booking
            from django.utils import timezone
            return Booking.objects.filter(
                photographer=self,
                date__gte=timezone.now().date(),
                status__in=['pending', 'confirmed']
            ).order_by('date', 'start_time')
        return None
    
    def get_recent_activity(self, limit=10):
        """آخر نشاط للمستخدم"""
        # يمكن ربطها مع نظام Audit Log
        return []
    
    def clean(self):
        """التحقق من صحة البيانات"""
        # التحقق من أن البريد الإلكتروني فريد
        if self.email:
            from django.db.models import Q
            if User.objects.filter(email=self.email).exclude(id=self.id).exists():
                from django.core.exceptions import ValidationError
                raise ValidationError({
                    'email': 'البريد الإلكتروني موجود بالفعل'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Class Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @classmethod
    def get_by_role(cls, role):
        """الحصول على المستخدمين حسب الدور"""
        return cls.objects.filter(role=role, is_active=True)
    
    @classmethod
    def get_photographers(cls):
        """الحصول على جميع المصورين النشطين"""
        return cls.get_by_role(cls.Roles.PHOTOGRAPHER)
    
    @classmethod
    def get_receptionists(cls):
        """الحصول على جميع موظفي الاستقبال"""
        return cls.get_by_role(cls.Roles.RECEPTIONIST)
    
    @classmethod
    def get_admins(cls):
        """الحصول على جميع المديرين"""
        return cls.get_by_role(cls.Roles.ADMIN)
    
    @classmethod
    def get_active_staff(cls):
        """الحصول على جميع الموظفين النشطين"""
        return cls.objects.filter(
            is_active=True,
            status=cls.Status.ACTIVE
        ).exclude(role=cls.Roles.ADMIN)