from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator


class Payment(models.Model):
    """
    نموذج المدفوعات الاحترافي
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 PAYMENT TYPE CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class PaymentTypes(models.TextChoices):
        DEPOSIT = 'deposit', 'دفعة مقدمة'
        INSTALLMENT = 'installment', 'قسط'
        FULL = 'full', 'دفعة كاملة'
        EXTRA = 'extra', 'دفعة إضافية'
        REMAINING = 'remaining', 'المتبقي'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 STATUS CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد الانتظار'
        PAID = 'paid', 'مدفوع'
        FAILED = 'failed', 'فشل'
        REFUNDED = 'refunded', 'مسترد'
        PARTIAL = 'partial', 'مدفوع جزئياً'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 PAYMENT METHOD CHOICES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'نقدي'
        BANK_TRANSFER = 'bank_transfer', 'تحويل بنكي'
        CREDIT_CARD = 'credit_card', 'بطاقة ائتمان'
        DEBIT_CARD = 'debit_card', 'بطاقة خصم'
        CHEQUE = 'cheque', 'شيك'
        MOBILE = 'mobile', 'محفظة إلكترونية'
        ONLINE = 'online', 'دفع إلكتروني'
        OTHER = 'other', 'أخرى'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Fields
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='الحجز'
    )
    
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_payments',
        verbose_name='تم الإنشاء بواسطة'
    )
    
    amount = models.DecimalField(
        'المبلغ',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='المبلغ المدفوع'
    )
    
    payment_type = models.CharField(
        'نوع الدفعة',
        max_length=20,
        choices=PaymentTypes.choices,
        db_index=True
    )
    
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
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
    # 🔹 Payment Details
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    reference_number = models.CharField(
        'رقم المرجع',
        max_length=100,
        blank=True,
        help_text='رقم المرجع من البنك أو المعاملة'
    )
    
    transaction_id = models.CharField(
        'رقم المعاملة',
        max_length=100,
        blank=True,
        db_index=True,
        help_text='رقم المعاملة من بوابة الدفع'
    )
    
    description = models.TextField(
        'الوصف',
        blank=True,
        help_text='وصف الدفعة (سبب الدفع، ملاحظات)'
    )
    
    receipt = models.FileField(
        'إيصال الدفع',
        upload_to='receipts/payments/%Y/%m/',
        null=True,
        blank=True,
        help_text='رفع صورة الإيصال أو إثبات الدفع'
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Dates
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    payment_date = models.DateTimeField(
        'تاريخ الدفع',
        default=timezone.now,
        db_index=True,
        help_text='تاريخ ووقت الدفع الفعلي'
    )
    
    due_date = models.DateTimeField(
        'تاريخ الاستحقاق',
        null=True,
        blank=True,
        help_text='تاريخ استحقاق الدفع'
    )
    
    confirmed_at = models.DateTimeField(
        'تاريخ التأكيد',
        null=True,
        blank=True,
        help_text='تاريخ تأكيد استلام الدفع'
    )
    
    refunded_at = models.DateTimeField(
        'تاريخ الاسترداد',
        null=True,
        blank=True,
        help_text='تاريخ استرداد المبلغ'
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
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Meta
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = 'دفعة'
        verbose_name_plural = 'المدفوعات'
        indexes = [
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['payment_type', 'status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['payment_date']),
        ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 String
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.amount:.2f} ({self.get_status_display()})"
    
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
    def is_failed(self):
        return self.status == self.Status.FAILED
    
    @property
    def is_refunded(self):
        return self.status == self.Status.REFUNDED
    
    @property
    def is_deposit(self):
        return self.payment_type == self.PaymentTypes.DEPOSIT
    
    @property
    def is_full(self):
        return self.payment_type == self.PaymentTypes.FULL
    
    @property
    def is_installment(self):
        return self.payment_type == self.PaymentTypes.INSTALLMENT
    
    @property
    def is_overdue(self):
        if self.due_date and self.status != self.Status.PAID:
            return self.due_date < timezone.now()
        return False
    
    @property
    def payment_type_display_ar(self):
        """عرض نوع الدفعة بالعربية"""
        return dict(self.PaymentTypes.choices).get(self.payment_type, self.payment_type)
    
    @property
    def status_display_ar(self):
        """عرض الحالة بالعربية"""
        return dict(self.Status.choices).get(self.status, self.status)
    
    @property
    def payment_method_display_ar(self):
        """عرض طريقة الدفع بالعربية"""
        return dict(self.PaymentMethod.choices).get(self.payment_method, self.payment_method)
    
    @property
    def customer_name(self):
        """اسم العميل"""
        return self.booking.customer.name if self.booking and self.booking.customer else '-'
    
    @property
    def photographer_name(self):
        """اسم المصور"""
        return self.booking.photographer.get_full_name() if self.booking and self.booking.photographer else '-'
    
    @property
    def booking_amount(self):
        """مبلغ الحجز الكلي"""
        return self.booking.price if self.booking else 0
    
    @property
    def remaining_balance(self):
        """المبلغ المتبقي للحجز"""
        if self.booking:
            total_paid = self.booking.payments.filter(
                status=self.Status.PAID
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            return self.booking.price - total_paid
        return 0
    
    @property
    def total_paid_for_booking(self):
        """إجمالي المدفوع للحجز"""
        return self.booking.payments.filter(
            status=self.Status.PAID
        ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def confirm(self, user=None):
        """تأكيد الدفع"""
        self.status = self.Status.PAID
        self.confirmed_at = timezone.now()
        self.save(update_fields=['status', 'confirmed_at'])
    
    def fail(self, user=None):
        """تسجيل فشل الدفع"""
        self.status = self.Status.FAILED
        self.save(update_fields=['status'])
    
    def refund(self, user=None):
        """استرداد الدفع"""
        if self.status != self.Status.PAID:
            raise ValidationError('لا يمكن استرداد دفعة غير مدفوعة')
        self.status = self.Status.REFUNDED
        self.refunded_at = timezone.now()
        self.save(update_fields=['status', 'refunded_at'])
    
    def mark_as_pending(self):
        """تغيير الحالة إلى قيد الانتظار"""
        self.status = self.Status.PENDING
        self.save(update_fields=['status'])
    
    def clean(self):
        """التحقق من صحة البيانات"""
        if self.amount <= 0:
            raise ValidationError({
                'amount': 'المبلغ يجب أن يكون أكبر من صفر'
            })
        
        # التحقق من أن المبلغ لا يتجاوز المتبقي من الحجز
        if self.booking and self.status != self.Status.REFUNDED:
            remaining = self.remaining_balance
            if remaining > 0 and self.amount > remaining and not self.is_full:
                raise ValidationError({
                    'amount': f'المبلغ ({self.amount}) يتجاوز المتبقي من الحجز ({remaining})'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Class Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @classmethod
    def get_total_by_booking(cls, booking_id):
        """إجمالي المدفوعات لحجز معين"""
        return cls.objects.filter(
            booking_id=booking_id,
            status=cls.Status.PAID
        ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    @classmethod
    def get_total_by_status(cls, status=None):
        """إجمالي المدفوعات حسب الحالة"""
        queryset = cls.objects.filter(status=status) if status else cls.objects.all()
        return queryset.aggregate(total=models.Sum('amount'))['total'] or 0
    
    @classmethod
    def get_total_by_date_range(cls, start_date, end_date):
        """إجمالي المدفوعات في نطاق تاريخي"""
        return cls.objects.filter(
            payment_date__range=[start_date, end_date],
            status=cls.Status.PAID
        ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    @classmethod
    def get_monthly_totals(cls, year=None, month=None):
        """إجمالي المدفوعات الشهرية"""
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month
        
        return cls.objects.filter(
            payment_date__year=year,
            payment_date__month=month,
            status=cls.Status.PAID
        ).aggregate(total=models.Sum('amount'))['total'] or 0