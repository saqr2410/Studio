from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import RegexValidator, EmailValidator


class Customer(models.Model):
    """
    نموذج العميل الاحترافي
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 GENDER CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_OTHER = 'other'
    
    GENDER_CHOICES = [
        (GENDER_MALE, 'ذكر'),
        (GENDER_FEMALE, 'أنثى'),
        (GENDER_OTHER, 'آخر'),
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 CUSTOMER TYPE CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    TYPE_REGULAR = 'regular'
    TYPE_VIP = 'vip'
    TYPE_CORPORATE = 'corporate'
    TYPE_AGENCY = 'agency'
    
    TYPE_CHOICES = [
        (TYPE_REGULAR, 'عميل عادي'),
        (TYPE_VIP, 'عميل VIP'),
        (TYPE_CORPORATE, 'شركة / مؤسسة'),
        (TYPE_AGENCY, 'وكالة / استوديو'),
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Basic Info
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    name = models.CharField(
        'الاسم',
        max_length=100,
        db_index=True
    )
    
    phone = models.CharField(
        'رقم الهاتف',
        max_length=20,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{10,15}$',
                message='رقم الهاتف يجب أن يكون صحيحاً (مثال: 0123456789 أو +201234567890)'
            )
        ],
        help_text='أدخل رقم الهاتف مع مفتاح الدولة (مثال: +201234567890)'
    )
    
    email = models.EmailField(
        'البريد الإلكتروني',
        blank=True,
        null=True,
        # unique=True,  # ✅ علق أو احذف هذا السطر
        validators=[EmailValidator()],
        help_text='البريد الإلكتروني للعميل (اختياري)'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Additional Info
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    gender = models.CharField(
        'الجنس',
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    
    customer_type = models.CharField(
        'نوع العميل',
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_REGULAR,
        db_index=True
    )
    
    date_of_birth = models.DateField(
        'تاريخ الميلاد',
        blank=True,
        null=True
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Address
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
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
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Social Media
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    instagram = models.URLField(
        'Instagram',
        blank=True,
        null=True,
        help_text='رابط حساب Instagram'
    )
    
    facebook = models.URLField(
        'Facebook',
        blank=True,
        null=True,
        help_text='رابط حساب Facebook'
    )
    
    twitter = models.URLField(
        'Twitter / X',
        blank=True,
        null=True
    )
    
    website = models.URLField(
        'الموقع الإلكتروني',
        blank=True,
        null=True
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Preferences
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    preferred_photographer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_customers',
        verbose_name='المصور المفضل'
    )
    
    preferred_package = models.ForeignKey(
        'packages.Package',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_by_customers',
        verbose_name='الباقة المفضلة'
    )
    
    preferred_contact_method = models.CharField(
        'طريقة التواصل المفضلة',
        max_length=20,
        choices=[
            ('phone', 'هاتف'),
            ('whatsapp', 'واتساب'),
            ('email', 'بريد إلكتروني'),
            ('sms', 'رسالة نصية'),
        ],
        default='phone'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Notes & Meta
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    notes = models.TextField(
        'ملاحظات',
        blank=True,
        help_text='ملاحظات إضافية عن العميل'
    )
    
    is_active = models.BooleanField(
        'نشط',
        default=True,
        db_index=True
    )
    
    is_blacklisted = models.BooleanField(
        'محظور',
        default=False,
        db_index=True,
        help_text='تعطيل العميل ومنعه من الحجز'
    )
    
    blacklist_reason = models.TextField(
        'سبب الحظر',
        blank=True,
        help_text='سبب حظر العميل إن وجد'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Statistics (cached)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    total_bookings = models.PositiveIntegerField(
        'إجمالي الحجوزات',
        default=0
    )
    
    total_spent = models.DecimalField(
        'إجمالي المصروفات',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    last_booking_date = models.DateTimeField(
        'تاريخ آخر حجز',
        blank=True,
        null=True
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Timestamps
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
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
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers_created',
        verbose_name='تم الإنشاء بواسطة'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Meta
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'عميل'
        verbose_name_plural = 'العملاء'
        indexes = [
            models.Index(fields=['name', 'phone']),
            models.Index(fields=['customer_type', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 String Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def __str__(self):
        return self.name
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Properties
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @property
    def full_name(self):
        """الاسم الكامل"""
        return self.name
    
    @property
    def is_vip(self):
        """تحقق إذا كان العميل VIP"""
        return self.customer_type == self.TYPE_VIP
    
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
    def booking_count(self):
        """عدد الحجوزات"""
        return self.total_bookings or self.bookings.count()
    
    @property
    def total_revenue(self):
        """إجمالي الإيرادات من العميل"""
        if self.total_spent:
            return self.total_spent
        return self.bookings.filter(status='done').aggregate(
            total=models.Sum('price')
        )['total'] or 0
    
    @property
    def display_phone(self):
        """عرض رقم الهاتف بشكل منسق"""
        phone = self.phone
        if phone and len(phone) >= 10:
            return f"{phone[:3]}****{phone[-4:]}"
        return phone
    
    @property
    def contact_info(self):
        """معلومات الاتصال للعرض"""
        info = []
        if self.phone:
            info.append(f"📞 {self.phone}")
        if self.email:
            info.append(f"✉️ {self.email}")
        return " | ".join(info)
    
    @property
    def status_badge(self):
        """Badge الحالة"""
        if self.is_blacklisted:
            return 'محظور'
        if not self.is_active:
            return 'غير نشط'
        if self.is_vip:
            return 'VIP ⭐'
        return 'نشط'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def update_stats(self):
        """تحديث إحصائيات العميل"""
        from django.db.models import Count, Sum
        
        stats = self.bookings.aggregate(
            total=Count('id'),
            spent=Sum('price', filter=models.Q(status='done'))
        )
        
        self.total_bookings = stats['total'] or 0
        self.total_spent = stats['spent'] or 0
        
        last_booking = self.bookings.order_by('-date', '-start_time').first()
        self.last_booking_date = last_booking.created_at if last_booking else None
        
        self.save(update_fields=['total_bookings', 'total_spent', 'last_booking_date'])
    
    def get_recent_bookings(self, limit=5):
        """الحصول على أحدث الحجوزات"""
        return self.bookings.select_related('photographer').order_by('-date', '-start_time')[:limit]
    
    def get_upcoming_bookings(self):
        """الحصول على الحجوزات القادمة"""
        return self.bookings.filter(
            date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).order_by('date', 'start_time')
    
    def get_favorite_photographer(self):
        """المصور الأكثر استخداماً من قبل العميل"""
        from django.db.models import Count
        favorite = self.bookings.values('photographer').annotate(
            count=Count('photographer')
        ).order_by('-count').first()
        if favorite:
            from users.models import User
            return User.objects.get(id=favorite['photographer'])
        return None
    
    def clean(self):
        """التحقق من صحة البيانات"""
        # التحقق من أن رقم الهاتف فريد
        if self.phone:
            qs = Customer.objects.exclude(id=self.id)
            if qs.filter(phone=self.phone).exists():
                raise ValidationError({
                    'phone': 'رقم الهاتف موجود بالفعل'
                })
        
        # ✅ التحقق من أن البريد الإلكتروني فريد فقط لو مش فاضي
        if self.email and self.email.strip():  # ✅ التعديل هنا
            qs = Customer.objects.exclude(id=self.id)
            if qs.filter(email=self.email).exists():
                raise ValidationError({
                    'email': 'البريد الإلكتروني موجود بالفعل'
                })
        
        # التحقق من أن العميل المحظور لديه سبب
        if self.is_blacklisted and not self.blacklist_reason:
            raise ValidationError({
                'blacklist_reason': 'يجب إدخال سبب الحظر'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Class Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @classmethod
    def get_active_customers(cls):
        """الحصول على العملاء النشطين"""
        return cls.objects.filter(is_active=True, is_blacklisted=False)
    
    @classmethod
    def get_vip_customers(cls):
        """الحصول على عملاء VIP"""
        return cls.objects.filter(customer_type=cls.TYPE_VIP, is_active=True)
    
    @classmethod
    def search_customers(cls, query):
        """البحث في العملاء"""
        from django.db.models import Q
        return cls.objects.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )