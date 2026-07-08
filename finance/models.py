from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator


class Expense(models.Model):
    """
    نموذج المصروفات الاحترافي
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 CATEGORY CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Category(models.TextChoices):
        EQUIPMENT = 'equipment', 'معدات'
        SALARY = 'salary', 'رواتب'
        RENT = 'rent', 'إيجار'
        UTILITIES = 'utilities', 'مرافق'
        MARKETING = 'marketing', 'تسويق'
        SOFTWARE = 'software', 'برمجيات'
        MAINTENANCE = 'maintenance', 'صيانة'
        TRAVEL = 'travel', 'سفر'
        SUPPLIES = 'supplies', 'لوازم'
        TAX = 'tax', 'ضرائب'
        OTHER = 'other', 'أخرى'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 PAYMENT METHOD CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'نقدي'
        BANK = 'bank', 'تحويل بنكي'
        CREDIT = 'credit', 'بطاقة ائتمان'
        CHEQUE = 'cheque', 'شيك'
        OTHER = 'other', 'أخرى'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 STATUS CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد الانتظار'
        PAID = 'paid', 'مدفوع'
        CANCELLED = 'cancelled', 'ملغي'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Fields
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    title = models.CharField(
        'عنوان المصروف',
        max_length=200,
        db_index=True
    )
    
    description = models.TextField(
        'الوصف',
        blank=True,
        help_text='وصف تفصيلي للمصروف'
    )
    
    amount = models.DecimalField(
        'المبلغ',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='المبلغ بالعملة المحلية'
    )
    
    category = models.CharField(
        'التصنيف',
        max_length=50,
        choices=Category.choices,
        db_index=True
    )
    
    payment_method = models.CharField(
        'طريقة الدفع',
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        db_index=True
    )
    
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Related
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    project = models.ForeignKey(
        'reports.Report',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        verbose_name='المشروع'
    )
    
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        verbose_name='الحجز'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Receipt
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    receipt = models.FileField(
        'إيصال',
        upload_to='receipts/expenses/%Y/%m/',
        null=True,
        blank=True,
        help_text='رفع صورة الإيصال (PDF أو صورة)'
    )
    
    receipt_number = models.CharField(
        'رقم الإيصال',
        max_length=50,
        blank=True,
        help_text='رقم الإيصال من المورد'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Vendor
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    vendor = models.CharField(
        'المورد',
        max_length=200,
        blank=True,
        help_text='اسم المورد أو الشخص المستحق'
    )
    
    vendor_phone = models.CharField(
        'هاتف المورد',
        max_length=20,
        blank=True
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Dates
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    expense_date = models.DateField(
        'تاريخ المصروف',
        default=timezone.now,
        db_index=True,
        help_text='تاريخ حدوث المصروف'
    )
    
    due_date = models.DateField(
        'تاريخ الاستحقاق',
        null=True,
        blank=True,
        help_text='تاريخ استحقاق الدفع (للفواتير)'
    )
    
    paid_date = models.DateTimeField(
        'تاريخ الدفع',
        null=True,
        blank=True
    )
    
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
        related_name='expenses_created',
        verbose_name='تم الإنشاء بواسطة'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Meta
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
        verbose_name = 'مصروف'
        verbose_name_plural = 'المصروفات'
        indexes = [
            models.Index(fields=['category', 'expense_date']),
            models.Index(fields=['status', 'expense_date']),
            models.Index(fields=['project', 'status']),
        ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 String
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def __str__(self):
        return f"{self.title} - {self.amount:.2f} ({self.get_category_display()})"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Properties
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @property
    def is_paid(self):
        return self.status == self.Status.PAID
    
    @property
    def is_pending(self):
        return self.status == self.Status.PENDING
    
    @property
    def is_overdue(self):
        if self.due_date and self.status != self.Status.PAID:
            return self.due_date < timezone.now().date()
        return False
    
    @property
    def category_display_ar(self):
        """عرض التصنيف بالعربية"""
        return dict(self.Category.choices).get(self.category, self.category)
    
    @property
    def status_display_ar(self):
        """عرض الحالة بالعربية"""
        return dict(self.Status.choices).get(self.status, self.status)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def mark_paid(self):
        """تحديث المصروف كمدفوع"""
        self.status = self.Status.PAID
        self.paid_date = timezone.now()
        self.save(update_fields=['status', 'paid_date'])
    
    def cancel(self):
        """إلغاء المصروف"""
        self.status = self.Status.CANCELLED
        self.save(update_fields=['status'])
    
    def clean(self):
        """التحقق من صحة البيانات"""
        if self.amount <= 0:
            raise ValidationError({
                'amount': 'المبلغ يجب أن يكون أكبر من صفر'
            })
        
        if self.due_date and self.expense_date and self.due_date < self.expense_date:
            raise ValidationError({
                'due_date': 'تاريخ الاستحقاق لا يمكن أن يكون قبل تاريخ المصروف'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Class Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @classmethod
    def get_total_by_category(cls, start_date=None, end_date=None):
        """إجمالي المصروفات حسب التصنيف"""
        from django.db.models import Sum
        queryset = cls.objects.filter(status=cls.Status.PAID)
        if start_date:
            queryset = queryset.filter(expense_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(expense_date__lte=end_date)
        
        return queryset.values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')
    
    @classmethod
    def get_monthly_totals(cls, year=None, month=None):
        """إجمالي المصروفات الشهرية"""
        from django.db.models import Sum
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month
        
        return cls.objects.filter(
            status=cls.Status.PAID,
            expense_date__year=year,
            expense_date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0


class Income(models.Model):
    """
    نموذج الإيرادات الاحترافي
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 SOURCE CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Source(models.TextChoices):
        BOOKING = 'booking', 'حجز تصوير'
        PACKAGE = 'package', 'باقة تصوير'
        PRINT = 'print', 'مطبوعات'
        DIGITAL = 'digital', 'ملفات رقمية'
        ALBUM = 'album', 'ألبوم صور'
        FRAMING = 'framing', 'تأطير'
        STUDIO_RENT = 'studio_rent', 'تأجير استوديو'
        WORKSHOP = 'workshop', 'ورشة عمل'
        OTHER = 'other', 'أخرى'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 PAYMENT METHOD CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'نقدي'
        BANK = 'bank', 'تحويل بنكي'
        CREDIT = 'credit', 'بطاقة ائتمان'
        CHEQUE = 'cheque', 'شيك'
        ONLINE = 'online', 'دفع إلكتروني'
        OTHER = 'other', 'أخرى'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Fields
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    title = models.CharField(
        'عنوان الإيراد',
        max_length=200,
        blank=True,
        help_text='عنوان الإيراد (يُملأ تلقائياً من الحجز إن لم يُحدد)'
    )
    
    amount = models.DecimalField(
        'المبلغ',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='المبلغ بالعملة المحلية'
    )
    
    source = models.CharField(
        'المصدر',
        max_length=50,
        choices=Source.choices,
        default=Source.BOOKING,
        db_index=True
    )
    
    payment_method = models.CharField(
        'طريقة الدفع',
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        db_index=True
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Related
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incomes',
        verbose_name='الحجز'
    )
    
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incomes',
        verbose_name='العميل'
    )
    
    project = models.ForeignKey(
        'reports.Report',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incomes',
        verbose_name='المشروع'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Invoice
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    invoice_number = models.CharField(
        'رقم الفاتورة',
        max_length=50,
        blank=True,
        help_text='رقم الفاتورة الصادر'
    )
    
    invoice_file = models.FileField(
        'ملف الفاتورة',
        upload_to='invoices/%Y/%m/',
        null=True,
        blank=True
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Notes
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    description = models.TextField(
        'الوصف',
        blank=True,
        help_text='وصف تفصيلي للإيراد'
    )
    
    notes = models.TextField(
        'ملاحظات',
        blank=True
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Dates
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    income_date = models.DateField(
        'تاريخ الإيراد',
        default=timezone.now,
        db_index=True
    )
    
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
        related_name='incomes_created',
        verbose_name='تم الإنشاء بواسطة'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Meta
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Meta:
        ordering = ['-income_date', '-created_at']
        verbose_name = 'إيراد'
        verbose_name_plural = 'الإيرادات'
        indexes = [
            models.Index(fields=['source', 'income_date']),
            models.Index(fields=['booking', 'source']),
            models.Index(fields=['customer', 'income_date']),
        ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 String
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def __str__(self):
        return f"{self.title or 'إيراد'} - {self.amount:.2f} ({self.get_source_display()})"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Properties
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @property
    def source_display_ar(self):
        """عرض المصدر بالعربية"""
        return dict(self.Source.choices).get(self.source, self.source)
    
    @property
    def payment_method_display_ar(self):
        """عرض طريقة الدفع بالعربية"""
        return dict(self.PaymentMethod.choices).get(self.payment_method, self.payment_method)
    
    @property
    def is_from_booking(self):
        """هل الإيراد من حجز"""
        return self.source == self.Source.BOOKING
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def clean(self):
        """التحقق من صحة البيانات"""
        if self.amount <= 0:
            raise ValidationError({
                'amount': 'المبلغ يجب أن يكون أكبر من صفر'
            })
    
    def save(self, *args, **kwargs):
        # تعيين العنوان تلقائياً من الحجز إن لم يُحدد
        if not self.title and self.booking:
            self.title = f"إيراد حجز {self.booking.id} - {self.booking.customer}"
        self.full_clean()
        super().save(*args, **kwargs)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Class Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @classmethod
    def get_total_by_source(cls, start_date=None, end_date=None):
        """إجمالي الإيرادات حسب المصدر"""
        from django.db.models import Sum
        queryset = cls.objects.all()
        if start_date:
            queryset = queryset.filter(income_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(income_date__lte=end_date)
        
        return queryset.values('source').annotate(
            total=Sum('amount')
        ).order_by('-total')
    
    @classmethod
    def get_monthly_totals(cls, year=None, month=None):
        """إجمالي الإيرادات الشهرية"""
        from django.db.models import Sum
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month
        
        return cls.objects.filter(
            income_date__year=year,
            income_date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0