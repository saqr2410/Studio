from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone
from .models import Expense, Income


class BaseFinanceAdmin:
    """كلاس أساسي لإدارة المصروفات والإيرادات"""
    
    list_per_page = 50
    
    def get_readonly_fields(self, request, obj=None):
        readonly = ['created_at', 'updated_at']
        if obj:  # عند التعديل
            readonly.append('created_by')
        return readonly
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 EXPENSE ADMIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@admin.register(Expense)
class ExpenseAdmin(BaseFinanceAdmin, admin.ModelAdmin):
    """
    إدارة المصروفات في Django Admin
    """
    
    list_display = [
        'id', 'title_display', 'amount_display', 'category_badge',
        'expense_date', 'payment_method_badge', 'status_badge',
        'vendor_short', 'created_at_short'
    ]
    
    list_display_links = ['id', 'title_display']
    
    list_filter = [
        'category', 'status', 'payment_method',
        ('expense_date', admin.DateFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
        'project',
    ]
    
    search_fields = [
        'id', 'title', 'description', 'vendor',
        'receipt_number', 'vendor_phone'
    ]
    
    ordering = ['-expense_date', '-created_at']
    
    fieldsets = (
        ('📋 معلومات المصروف', {
            'fields': (
                ('title', 'amount'),
                ('category', 'payment_method'),
                'description',
            ),
        }),
        ('🏢 المورد', {
            'fields': (
                ('vendor', 'vendor_phone'),
            ),
            'classes': ('collapse',),
        }),
        ('📎 المرفقات', {
            'fields': (
                ('receipt', 'receipt_number'),
            ),
            'classes': ('collapse',),
        }),
        ('🔗 مرتبط بـ', {
            'fields': (
                ('project', 'booking'),
            ),
            'classes': ('collapse',),
        }),
        ('📅 التواريخ والحالة', {
            'fields': (
                ('expense_date', 'due_date'),
                ('status', 'paid_date'),
            ),
        }),
        ('📊 التواريخ الإدارية', {
            'fields': (
                ('created_at', 'updated_at'),
                'created_by',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'paid_date', 'created_by']
    
    actions = [
        'mark_as_paid', 'mark_as_pending', 'cancel_selected',
        'export_as_csv'
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status__in=['pending', 'cancelled']).update(
            status=Expense.Status.PAID,
            paid_date=timezone.now()
        )
        self.message_user(request, f'تم تحديث {updated} مصروف كمدفوع')
    mark_as_paid.short_description = 'تحديد كمدفوع ✅'
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.filter(status=Expense.Status.PAID).update(
            status=Expense.Status.PENDING,
            paid_date=None
        )
        self.message_user(request, f'تم تحديث {updated} مصروف كقيد الانتظار')
    mark_as_pending.short_description = 'تحديد كقيد الانتظار ⏳'
    
    def cancel_selected(self, request, queryset):
        updated = queryset.filter(status=Expense.Status.PENDING).update(
            status=Expense.Status.CANCELLED
        )
        self.message_user(request, f'تم إلغاء {updated} مصروف')
    cancel_selected.short_description = 'إلغاء المصروفات المحددة ❌'
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'العنوان', 'المبلغ', 'التصنيف', 'طريقة الدفع',
            'الحالة', 'تاريخ المصروف', 'المورد'
        ])
        
        for expense in queryset:
            writer.writerow([
                expense.id,
                expense.title,
                expense.amount,
                expense.get_category_display(),
                expense.get_payment_method_display(),
                expense.get_status_display(),
                expense.expense_date,
                expense.vendor or '',
            ])
        
        return response
    export_as_csv.short_description = 'تصدير CSV 📄'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Display Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @admin.display(description='العنوان')
    def title_display(self, obj):
        if len(obj.title) > 30:
            return f'{obj.title[:30]}...'
        return obj.title
    
    @admin.display(description='المبلغ')
    def amount_display(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #dc3545;">💰 {:.2f}</span>',
            obj.amount
        )
    
    @admin.display(description='التصنيف')
    def category_badge(self, obj):
        colors = {
            Expense.Category.EQUIPMENT: '#007bff',
            Expense.Category.SALARY: '#28a745',
            Expense.Category.RENT: '#fd7e14',
            Expense.Category.UTILITIES: '#6f42c1',
            Expense.Category.MARKETING: '#e83e8c',
            Expense.Category.SOFTWARE: '#20c997',
            Expense.Category.MAINTENANCE: '#ffc107',
            Expense.Category.TRAVEL: '#17a2b8',
            Expense.Category.SUPPLIES: '#6c757d',
            Expense.Category.TAX: '#dc3545',
            Expense.Category.OTHER: '#6c757d',
        }
        color = colors.get(obj.category, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_category_display()
        )
    
    @admin.display(description='طريقة الدفع')
    def payment_method_badge(self, obj):
        colors = {
            Expense.PaymentMethod.CASH: '#28a745',
            Expense.PaymentMethod.BANK: '#007bff',
            Expense.PaymentMethod.CREDIT: '#fd7e14',
            Expense.PaymentMethod.CHEQUE: '#6c757d',
            Expense.PaymentMethod.OTHER: '#6c757d',
        }
        color = colors.get(obj.payment_method, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">{}</span>',
            color,
            obj.get_payment_method_display()
        )
    
    @admin.display(description='الحالة')
    def status_badge(self, obj):
        if obj.status == Expense.Status.PAID:
            color = '#28a745'
            icon = '✅'
        elif obj.status == Expense.Status.PENDING:
            color = '#ffc107'
            icon = '⏳'
        else:
            color = '#dc3545'
            icon = '❌'
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 2px 12px; border-radius: 12px; font-size: 0.85em;">{} {}</span>',
            color,
            '#000' if obj.status == Expense.Status.PENDING else '#fff',
            icon,
            obj.get_status_display()
        )
    
    @admin.display(description='المورد')
    def vendor_short(self, obj):
        if obj.vendor:
            if len(obj.vendor) > 20:
                return f'{obj.vendor[:20]}...'
            return obj.vendor
        return '-'
    
    @admin.display(description='التاريخ')
    def created_at_short(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 INCOME ADMIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@admin.register(Income)
class IncomeAdmin(BaseFinanceAdmin, admin.ModelAdmin):
    """
    إدارة الإيرادات في Django Admin
    """
    
    list_display = [
        'id', 'title_display', 'amount_display', 'source_badge',
        'income_date', 'payment_method_badge', 'customer_short',
        'booking_id_display', 'created_at_short'
    ]
    
    list_display_links = ['id', 'title_display']
    
    list_filter = [
        'source', 'payment_method',
        ('income_date', admin.DateFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
        'booking',
        'customer',
    ]
    
    search_fields = [
        'id', 'title', 'description', 'notes',
        'invoice_number', 'customer__name', 'customer__phone'
    ]
    
    ordering = ['-income_date', '-created_at']
    
    fieldsets = (
        ('📋 معلومات الإيراد', {
            'fields': (
                ('title', 'amount'),
                ('source', 'payment_method'),
                'description',
            ),
        }),
        ('🔗 مرتبط بـ', {
            'fields': (
                ('booking', 'customer', 'project'),
            ),
            'classes': ('collapse',),
        }),
        ('📎 الفاتورة', {
            'fields': (
                ('invoice_number', 'invoice_file'),
            ),
            'classes': ('collapse',),
        }),
        ('📝 ملاحظات', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
        ('📅 التواريخ', {
            'fields': (
                ('income_date', 'created_at', 'updated_at'),
                'created_by',
            ),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    actions = ['export_as_csv']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="incomes.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'العنوان', 'المبلغ', 'المصدر', 'طريقة الدفع',
            'العميل', 'تاريخ الإيراد'
        ])
        
        for income in queryset:
            writer.writerow([
                income.id,
                income.title or '',
                income.amount,
                income.get_source_display(),
                income.get_payment_method_display(),
                str(income.customer) if income.customer else '',
                income.income_date,
            ])
        
        return response
    export_as_csv.short_description = 'تصدير CSV 📄'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Display Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @admin.display(description='العنوان')
    def title_display(self, obj):
        if obj.title:
            if len(obj.title) > 30:
                return f'{obj.title[:30]}...'
            return obj.title
        return f'إيراد #{obj.id}'
    
    @admin.display(description='المبلغ')
    def amount_display(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">💰 {:.2f}</span>',
            obj.amount
        )
    
    @admin.display(description='المصدر')
    def source_badge(self, obj):
        colors = {
            Income.Source.BOOKING: '#007bff',
            Income.Source.PACKAGE: '#28a745',
            Income.Source.PRINT: '#fd7e14',
            Income.Source.DIGITAL: '#6f42c1',
            Income.Source.ALBUM: '#e83e8c',
            Income.Source.FRAMING: '#20c997',
            Income.Source.STUDIO_RENT: '#17a2b8',
            Income.Source.WORKSHOP: '#ffc107',
            Income.Source.OTHER: '#6c757d',
        }
        color = colors.get(obj.source, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_source_display()
        )
    
    @admin.display(description='طريقة الدفع')
    def payment_method_badge(self, obj):
        colors = {
            Income.PaymentMethod.CASH: '#28a745',
            Income.PaymentMethod.BANK: '#007bff',
            Income.PaymentMethod.CREDIT: '#fd7e14',
            Income.PaymentMethod.CHEQUE: '#6c757d',
            Income.PaymentMethod.ONLINE: '#17a2b8',
            Income.PaymentMethod.OTHER: '#6c757d',
        }
        color = colors.get(obj.payment_method, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">{}</span>',
            color,
            obj.get_payment_method_display()
        )
    
    @admin.display(description='العميل')
    def customer_short(self, obj):
        if obj.customer:
            return obj.customer.name
        if obj.booking and obj.booking.customer:
            return obj.booking.customer.name
        return '-'
    
    @admin.display(description='الحجز')
    def booking_id_display(self, obj):
        if obj.booking:
            return format_html(
                '<a href="/admin/bookings/booking/{}/change/">#{}</a>',
                obj.booking.id,
                obj.booking.id
            )
        return '-'
    
    @admin.display(description='التاريخ')
    def created_at_short(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')