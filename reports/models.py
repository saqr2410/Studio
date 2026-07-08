from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class Report(models.Model):
    """
    نموذج التقارير الرئيسي
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 REPORT TYPES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Type(models.TextChoices):
        BOOKING = 'booking', 'تقرير حجوزات'
        FINANCIAL = 'financial', 'تقرير مالي'
        CUSTOMER = 'customer', 'تقرير عملاء'
        PHOTOGRAPHER = 'photographer', 'تقرير مصورين'
        PAYMENT = 'payment', 'تقرير مدفوعات'
        EXPENSE = 'expense', 'تقرير مصروفات'
        PROFIT = 'profit', 'تقرير أرباح'
        DAILY = 'daily', 'تقرير يومي'
        WEEKLY = 'weekly', 'تقرير أسبوعي'
        MONTHLY = 'monthly', 'تقرير شهري'
        YEARLY = 'yearly', 'تقرير سنوي'
        CUSTOM = 'custom', 'تقرير مخصص'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 FORMATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Format(models.TextChoices):
        PDF = 'pdf', 'PDF'
        EXCEL = 'excel', 'Excel'
        CSV = 'csv', 'CSV'
        JSON = 'json', 'JSON'
        HTML = 'html', 'HTML'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 STATUS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد الإنشاء'
        PROCESSING = 'processing', 'جاري التجهيز'
        COMPLETED = 'completed', 'مكتمل'
        FAILED = 'failed', 'فشل'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Fields
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # ── معلومات التقرير ──
    title = models.CharField(
        'عنوان التقرير',
        max_length=255,
        db_index=True
    )
    
    report_type = models.CharField(
        'نوع التقرير',
        max_length=20,
        choices=Type.choices,
        db_index=True
    )
    
    format = models.CharField(
        'صيغة التقرير',
        max_length=10,
        choices=Format.choices,
        default=Format.PDF
    )
    
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    # ── نطاق التقرير ──
    start_date = models.DateTimeField(
        'تاريخ البداية',
        null=True,
        blank=True
    )
    
    end_date = models.DateTimeField(
        'تاريخ النهاية',
        null=True,
        blank=True
    )
    
    # ── الفلاتر ──
    filters = models.JSONField(
        'الفلاتر',
        default=dict,
        blank=True,
        help_text='فلاتر إضافية للتقرير (مثل: photographer_id, customer_id, status)'
    )
    
    # ── البيانات ──
    data = models.JSONField(
        'البيانات',
        default=dict,
        blank=True,
        help_text='بيانات التقرير المستخرجة'
    )
    
    summary = models.JSONField(
        'الملخص',
        default=dict,
        blank=True,
        help_text='ملخص التقرير (إجمالي، متوسط، عدد...)'
    )
    
    # ── الملفات ──
    file = models.FileField(
        'ملف التقرير',
        upload_to='reports/%Y/%m/',
        null=True,
        blank=True
    )
    
    # ── ملاحظات ──
    notes = models.TextField(
        'ملاحظات',
        blank=True
    )
    
    # ── العلاقات ──
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_reports',
        verbose_name='تم الإنشاء بواسطة'
    )
    
    # ── التواريخ ──
    generated_at = models.DateTimeField(
        'تاريخ الإنشاء',
        auto_now_add=True,
        db_index=True
    )
    
    completed_at = models.DateTimeField(
        'تاريخ الاكتمال',
        null=True,
        blank=True
    )
    
    updated_at = models.DateTimeField(
        'آخر تحديث',
        auto_now=True
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Meta
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'تقرير'
        verbose_name_plural = 'التقارير'
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['created_by', 'generated_at']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 String
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Properties
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED
    
    @property
    def is_processing(self):
        return self.status == self.Status.PROCESSING
    
    @property
    def report_type_display_ar(self):
        return dict(self.Type.choices).get(self.report_type, self.report_type)
    
    @property
    def format_display_ar(self):
        return dict(self.Format.choices).get(self.format, self.format)
    
    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0
    
    @property
    def file_url(self):
        if self.file:
            return self.file.url
        return None
    
    @property
    def file_size(self):
        if self.file:
            return self.file.size
        return 0
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def mark_processing(self):
        self.status = self.Status.PROCESSING
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_completed(self, data=None, summary=None, file=None):
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if data is not None:
            self.data = data
        if summary is not None:
            self.summary = summary
        if file is not None:
            self.file = file
        self.save(update_fields=['status', 'completed_at', 'data', 'summary', 'file', 'updated_at'])
    
    def mark_failed(self, error_message=None):
        self.status = self.Status.FAILED
        if error_message:
            self.notes = error_message
        self.save(update_fields=['status', 'notes', 'updated_at'])
    
    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({
                    'end_date': 'تاريخ النهاية يجب أن يكون بعد تاريخ البداية'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ReportTemplate(models.Model):
    """
    قوالب التقارير
    """
    
    name = models.CharField(
        'اسم القالب',
        max_length=255,
        db_index=True
    )
    
    report_type = models.CharField(
        'نوع التقرير',
        max_length=20,
        choices=Report.Type.choices
    )
    
    description = models.TextField(
        'الوصف',
        blank=True
    )
    
    config = models.JSONField(
        'إعدادات القالب',
        default=dict,
        help_text='إعدادات التقرير (أعمدة، تنسيق، فلاتر افتراضية)'
    )
    
    is_default = models.BooleanField(
        'افتراضي',
        default=False
    )
    
    is_active = models.BooleanField(
        'نشط',
        default=True
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='report_templates'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', 'name']
        verbose_name = 'قالب تقرير'
        verbose_name_plural = 'قوالب التقارير'
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class ReportSchedule(models.Model):
    """
    جدولة التقارير
    """
    
    class Frequency(models.TextChoices):
        DAILY = 'daily', 'يومي'
        WEEKLY = 'weekly', 'أسبوعي'
        MONTHLY = 'monthly', 'شهري'
        QUARTERLY = 'quarterly', 'ربع سنوي'
        YEARLY = 'yearly', 'سنوي'
    
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    frequency = models.CharField(
        'التكرار',
        max_length=20,
        choices=Frequency.choices
    )
    
    day_of_week = models.IntegerField(
        'يوم الأسبوع',
        null=True,
        blank=True,
        help_text='0=الأحد, 1=الاثنين, ...'
    )
    
    day_of_month = models.IntegerField(
        'يوم الشهر',
        null=True,
        blank=True,
        help_text='1-31'
    )
    
    time = models.TimeField(
        'الوقت',
        default='09:00'
    )
    
    recipients = models.JSONField(
        'المستلمين',
        default=list,
        help_text='قائمة البريد الإلكتروني للمستلمين'
    )
    
    is_active = models.BooleanField(
        'نشط',
        default=True
    )
    
    last_run = models.DateTimeField(
        'آخر تشغيل',
        null=True,
        blank=True
    )
    
    next_run = models.DateTimeField(
        'التشغيل القادم',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['next_run']
        verbose_name = 'جدول تقرير'
        verbose_name_plural = 'جداول التقارير'
    
    def __str__(self):
        return f"{self.report.title} - {self.get_frequency_display()}"