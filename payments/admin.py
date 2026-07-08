from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    إدارة المدفوعات في Django Admin
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 List Display
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    list_display = [
        'id',
        'booking_link',
        'amount_display',
        'payment_type_badge',
        'status_badge',
        'payment_method_badge',
        'payment_date_short',
        'customer_name',
    ]
    
    list_display_links = ['id', 'booking_link']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Filters
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    list_filter = [
        'status',
        'payment_type',
        'payment_method',
        ('payment_date', admin.DateFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
        'booking',
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Search
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    search_fields = [
        'id',
        'reference_number',
        'transaction_id',
        'description',
        'booking__customer__name',
        'booking__customer__phone',
        'booking__id',
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Ordering
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    ordering = ['-payment_date', '-created_at']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Fieldsets
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    fieldsets = (
        ('📋 معلومات الدفعة', {
            'fields': (
                ('booking', 'created_by'),
                ('amount', 'payment_type'),
                ('status', 'payment_method'),
            ),
        }),
        ('📎 تفاصيل الدفع', {
            'fields': (
                ('reference_number', 'transaction_id'),
                'description',
                'receipt',
            ),
            'classes': ('collapse',),
        }),
        ('📅 التواريخ', {
            'fields': (
                ('payment_date', 'due_date'),
                ('confirmed_at', 'refunded_at'),
                ('created_at', 'updated_at'),
            ),
        }),
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Readonly Fields
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'refunded_at']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    actions = [
        'confirm_selected',
        'fail_selected',
        'refund_selected',
        'export_as_csv',
    ]
    
    def confirm_selected(self, request, queryset):
        """تأكيد المدفوعات المحددة"""
        updated = queryset.filter(status__in=['pending', 'partial']).update(
            status=Payment.Status.PAID,
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'تم تأكيد {updated} دفعة')
    confirm_selected.short_description = 'تأكيد المدفوعات المحددة ✅'
    
    def fail_selected(self, request, queryset):
        """تسجيل فشل المدفوعات المحددة"""
        updated = queryset.filter(status=Payment.Status.PENDING).update(
            status=Payment.Status.FAILED
        )
        self.message_user(request, f'تم تسجيل فشل {updated} دفعة')
    fail_selected.short_description = 'تسجيل فشل المدفوعات المحددة ❌'
    
    def refund_selected(self, request, queryset):
        """استرداد المدفوعات المحددة"""
        updated = queryset.filter(status=Payment.Status.PAID).update(
            status=Payment.Status.REFUNDED,
            refunded_at=timezone.now()
        )
        self.message_user(request, f'تم استرداد {updated} دفعة')
    refund_selected.short_description = 'استرداد المدفوعات المحددة 🔄'
    
    def export_as_csv(self, request, queryset):
        """تصدير المدفوعات كملف CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payments.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'الحجز', 'العميل', 'المبلغ', 'نوع الدفعة',
            'الحالة', 'طريقة الدفع', 'تاريخ الدفع'
        ])
        
        for payment in queryset:
            writer.writerow([
                payment.id,
                payment.booking.id if payment.booking else '',
                payment.customer_name,
                payment.amount,
                payment.get_payment_type_display(),
                payment.get_status_display(),
                payment.get_payment_method_display(),
                payment.payment_date.strftime('%Y-%m-%d %H:%M'),
            ])
        
        return response
    export_as_csv.short_description = 'تصدير CSV 📄'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Display Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @admin.display(description='الحجز')
    def booking_link(self, obj):
        if obj.booking:
            url = reverse('admin:bookings_booking_change', args=[obj.booking.id])
            return format_html(
                '<a href="{}">حجز #{} - {}</a>',
                url,
                obj.booking.id,
                obj.booking.customer.name if obj.booking.customer else ''
            )
        return '-'
    
    @admin.display(description='المبلغ')
    def amount_display(self, obj):
        color = '#28a745' if obj.status == Payment.Status.PAID else '#dc3545'
        return format_html(
            '<span style="font-weight: bold; color: {};">💰 {:.2f}</span>',
            color,
            obj.amount
        )
    
    @admin.display(description='نوع الدفعة')
    def payment_type_badge(self, obj):
        colors = {
            Payment.PaymentTypes.DEPOSIT: '#007bff',
            Payment.PaymentTypes.INSTALLMENT: '#fd7e14',
            Payment.PaymentTypes.FULL: '#28a745',
            Payment.PaymentTypes.EXTRA: '#6f42c1',
            Payment.PaymentTypes.REMAINING: '#20c997',
        }
        color = colors.get(obj.payment_type, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_payment_type_display()
        )
    
    @admin.display(description='الحالة')
    def status_badge(self, obj):
        colors = {
            Payment.Status.PENDING: '#ffc107',
            Payment.Status.PAID: '#28a745',
            Payment.Status.FAILED: '#dc3545',
            Payment.Status.REFUNDED: '#6c757d',
            Payment.Status.PARTIAL: '#17a2b8',
        }
        color = colors.get(obj.status, '#6c757d')
        icons = {
            Payment.Status.PENDING: '⏳',
            Payment.Status.PAID: '✅',
            Payment.Status.FAILED: '❌',
            Payment.Status.REFUNDED: '🔄',
            Payment.Status.PARTIAL: '📝',
        }
        icon = icons.get(obj.status, '')
        return format_html(
            '<span style="background: {}; color: {}; padding: 2px 12px; border-radius: 12px; font-size: 0.85em;">{} {}</span>',
            color,
            '#000' if obj.status == Payment.Status.PENDING else '#fff',
            icon,
            obj.get_status_display()
        )
    
    @admin.display(description='طريقة الدفع')
    def payment_method_badge(self, obj):
        colors = {
            Payment.PaymentMethod.CASH: '#28a745',
            Payment.PaymentMethod.BANK_TRANSFER: '#007bff',
            Payment.PaymentMethod.CREDIT_CARD: '#fd7e14',
            Payment.PaymentMethod.DEBIT_CARD: '#6f42c1',
            Payment.PaymentMethod.CHEQUE: '#6c757d',
            Payment.PaymentMethod.MOBILE: '#20c997',
            Payment.PaymentMethod.ONLINE: '#17a2b8',
            Payment.PaymentMethod.OTHER: '#6c757d',
        }
        color = colors.get(obj.payment_method, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">{}</span>',
            color,
            obj.get_payment_method_display()
        )
    
    @admin.display(description='تاريخ الدفع')
    def payment_date_short(self, obj):
        return obj.payment_date.strftime('%Y-%m-%d %H:%M')
    
    @admin.display(description='العميل')
    def customer_name(self, obj):
        if obj.booking and obj.booking.customer:
            return obj.booking.customer.name
        return '-'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Stats in Admin
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def changelist_view(self, request, extra_context=None):
        """إضافة إحصائيات إلى صفحة القائمة"""
        extra_context = extra_context or {}
        
        extra_context['stats'] = {
            'total': Payment.objects.aggregate(total=Sum('amount'))['total'] or 0,
            'paid': Payment.objects.filter(status=Payment.Status.PAID).aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'pending': Payment.objects.filter(status=Payment.Status.PENDING).aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'failed': Payment.objects.filter(status=Payment.Status.FAILED).aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'refunded': Payment.objects.filter(status=Payment.Status.REFUNDED).aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'count': Payment.objects.count(),
        }
        
        return super().changelist_view(request, extra_context=extra_context)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Save
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)