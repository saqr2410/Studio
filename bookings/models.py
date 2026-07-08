from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q


class Booking(models.Model):
    """نموذج الحجز الاحترافي"""
    
    # 🔹 Constants
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'
    STATUS_CANCELLED = 'cancelled'
    STATUS_NO_SHOW = 'no_show'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'قيد الانتظار'),
        (STATUS_CONFIRMED, 'مؤكد'),
        (STATUS_IN_PROGRESS, 'قيد التنفيذ'),
        (STATUS_DONE, 'منتهي'),
        (STATUS_CANCELLED, 'ملغي'),
        (STATUS_NO_SHOW, 'لم يحضر'),
    ]
    
    # 🔹 العلاقات
    customer = models.ForeignKey(
        'customers.Customer', 
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    photographer = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    
    # 🔹 معلومات الحجز
    title = models.CharField(
        'عنوان الحجز',
        max_length=255,
        blank=True,
        help_text="مثال: جلسة تصوير زفاف"
    )
    date = models.DateField('التاريخ')
    start_time = models.TimeField('وقت البداية')
    end_time = models.TimeField('وقت النهاية')
    duration_hours = models.DecimalField(
        'المدة بالساعات',
        max_digits=4, 
        decimal_places=1,
        blank=True,
        null=True,
        help_text="تحسب تلقائياً إذا تركت فارغة"
    )
    
    # 🔹 تفاصيل إضافية
    package = models.ForeignKey(
        'packages.Package',  # لو عندك حزمة تصوير
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    price = models.DecimalField(
        'السعر',
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    deposit = models.DecimalField(
        'الدفعة المقدمة',
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    notes = models.TextField('ملاحظات', blank=True)
    
    # 🔹 الحالة
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    
    # 🔹 الموقع
    location = models.CharField(
        'الموقع',
        max_length=255,
        blank=True,
        help_text="عنوان التصوير"
    )
    is_onsite = models.BooleanField('تصوير في الموقع', default=False)
    
    # 🔹 التذكير
    reminder_sent = models.BooleanField('تم إرسال التذكير', default=False)
    reminder_sent_at = models.DateTimeField('تاريخ إرسال التذكير', null=True, blank=True)
    
    # 🔹 التقييم
    rating = models.PositiveSmallIntegerField(
        'تقييم العميل',
        null=True, 
        blank=True,
        choices=[(i, f'{i} نجوم') for i in range(1, 6)]
    )
    feedback = models.TextField('ملاحظات العميل', blank=True)
    
    # 🔹 التواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)
    confirmed_at = models.DateTimeField('تاريخ التأكيد', null=True, blank=True)
    cancelled_at = models.DateTimeField('تاريخ الإلغاء', null=True, blank=True)
    completed_at = models.DateTimeField('تاريخ الانتهاء', null=True, blank=True)
    
    # 🔹 من قام بالإجراء
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings_created',
        verbose_name='تم الإنشاء بواسطة'
    )
    
    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = 'حجز'
        verbose_name_plural = 'الحجوزات'
        indexes = [
            models.Index(fields=['photographer', 'date']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['status', 'date']),
        ]
    
    def __str__(self):
        return f"{self.customer} - {self.date} ({self.start_time})"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Properties
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @property
    def is_confirmed(self):
        return self.status == self.STATUS_CONFIRMED
    
    @property
    def is_cancelled(self):
        return self.status == self.STATUS_CANCELLED
    
    @property
    def is_done(self):
        return self.status == self.STATUS_DONE
    
    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING
    
    @property
    def is_upcoming(self):
        """هل الحجز قادم في المستقبل"""
        if self.is_cancelled or self.is_done:
            return False
        booking_datetime = timezone.datetime.combine(self.date, self.start_time)
        return booking_datetime > timezone.now()
    
    @property
    def is_ongoing(self):
        """هل الحجز جارٍ الآن"""
        if self.is_cancelled or self.is_done:
            return False
        now = timezone.now()
        booking_start = timezone.datetime.combine(self.date, self.start_time)
        booking_end = timezone.datetime.combine(self.date, self.end_time)
        return booking_start <= now <= booking_end
    
    @property
    def total_price(self):
        """السعر الإجمالي شامل الضريبة إن وجدت"""
        # لو عندك ضريبة
        tax_rate = 0.14  # 14% VAT
        return self.price + (self.price * tax_rate)
    
    @property
    def remaining_payment(self):
        """المبلغ المتبقي"""
        return self.price - self.deposit
    
    @property
    def duration_in_hours(self):
        """حساب المدة بالساعات"""
        if self.duration_hours:
            return self.duration_hours
        start = timezone.datetime.combine(self.date, self.start_time)
        end = timezone.datetime.combine(self.date, self.end_time)
        diff = end - start
        return round(diff.total_seconds() / 3600, 1)
    
    @property
    def status_display(self):
        """عرض الحالة بالعربي"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def confirm(self, user=None):
        """تأكيد الحجز"""
        self.status = self.STATUS_CONFIRMED
        self.confirmed_at = timezone.now()
        self.save()
    
    def cancel(self, user=None):
        """إلغاء الحجز"""
        self.status = self.STATUS_CANCELLED
        self.cancelled_at = timezone.now()
        self.save()
    
    def complete(self, user=None):
        """إنهاء الحجز"""
        self.status = self.STATUS_DONE
        self.completed_at = timezone.now()
        self.save()
    
    def mark_no_show(self, user=None):
        """تسجيل عدم الحضور"""
        self.status = self.STATUS_NO_SHOW
        self.save()
    
    def send_reminder(self):
        """إرسال تذكير (للتكامل مع إشعارات)"""
        self.reminder_sent = True
        self.reminder_sent_at = timezone.now()
        self.save()
    
    def clean(self):
        """التحقق من صحة البيانات"""
        # 1. التأكد من أن وقت النهاية بعد البداية
        if self.end_time <= self.start_time:
            raise ValidationError({
                'end_time': 'وقت النهاية يجب أن يكون بعد وقت البداية'
            })
        
        # 2. التأكد من عدم وجود حجز متعارض
        conflicts = Booking.objects.filter(
            photographer=self.photographer,
            date=self.date,
            status__in=[self.STATUS_PENDING, self.STATUS_CONFIRMED, self.STATUS_IN_PROGRESS]
        ).exclude(id=self.id)
        
        for booking in conflicts:
            overlap = (
                self.start_time < booking.end_time and
                self.end_time > booking.start_time
            )
            if overlap:
                raise ValidationError({
                    'start_time': f'المصور محجوز في هذا الوقت مع {booking.customer}'
                })
        
        # 3. التأكد من أن التاريخ ليس في الماضي (للمستخدمين العاديين)
        if not self.pk and self.date < timezone.now().date():
            raise ValidationError({
                'date': 'لا يمكن الحجز في تاريخ سابق'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)