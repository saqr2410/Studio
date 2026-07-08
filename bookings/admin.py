from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.contrib.admin import SimpleListFilter
from .models import Booking


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 Custom Filters
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BookingStatusFilter(SimpleListFilter):
    """فلتر مخصص لحالة الحجز"""
    title = 'الحالة المتقدمة'
    parameter_name = 'advanced_status'
    
    def lookups(self, request, model_admin):
        return (
            ('upcoming', 'قادم'),
            ('ongoing', 'جاري الآن'),
            ('past', 'منتهي'),
            ('cancelled', 'ملغي'),
            ('pending', 'قيد الانتظار'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        today = now.date()
        
        if self.value() == 'upcoming':
            return queryset.filter(
                date__gte=today,
                status__in=['pending', 'confirmed']
            )
        if self.value() == 'ongoing':
            # حجوزات اليوم والوقت الحالي
            return queryset.filter(
                date=today,
                start_time__lte=now.time(),
                end_time__gte=now.time(),
                status__in=['pending', 'confirmed', 'in_progress']
            )
        if self.value() == 'past':
            return queryset.filter(
                Q(date__lt=today) | Q(status='done')
            )
        if self.value() == 'cancelled':
            return queryset.filter(status='cancelled')
        if self.value() == 'pending':
            return queryset.filter(status='pending')
        return queryset


class DateRangeFilter(SimpleListFilter):
    """فلتر نطاق تاريخي"""
    title = 'الفترة الزمنية'
    parameter_name = 'date_range'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'اليوم'),
            ('this_week', 'هذا الأسبوع'),
            ('this_month', 'هذا الشهر'),
            ('next_week', 'الأسبوع القادم'),
            ('next_month', 'الشهر القادم'),
        )
    
    def queryset(self, request, queryset):
        today = timezone.now().date()
        
        if self.value() == 'today':
            return queryset.filter(date=today)
        if self.value() == 'this_week':
            start = today - timezone.timedelta(days=today.weekday())
            end = start + timezone.timedelta(days=6)
            return queryset.filter(date__range=[start, end])
        if self.value() == 'this_month':
            return queryset.filter(date__year=today.year, date__month=today.month)
        if self.value() == 'next_week':
            start = today + timezone.timedelta(days=(7 - today.weekday()))
            end = start + timezone.timedelta(days=6)
            return queryset.filter(date__range=[start, end])
        if self.value() == 'next_month':
            next_month = today.month + 1
            year = today.year
            if next_month > 12:
                next_month = 1
                year += 1
            return queryset.filter(date__year=year, date__month=next_month)
        return queryset


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 Inline Admin (عرض مرتبط)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# لو عندك موديلات مرتبطة بالحجز زي Payments أو Notes
# class PaymentInline(admin.TabularInline):
#     model = Payment
#     extra = 0
#     fields = ['amount', 'payment_method', 'date', 'status']
#     readonly_fields = ['date']


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 Main Admin Class
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    إدارة احترافية للحجوزات في Django Admin
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 List Display (عرض الجدول)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    list_display = [
        'id',
        'customer_link',
        'photographer_link',
        'date_display',
        'time_display',
        'duration_badge',
        'status_badge',
        'price_display',
        'created_ago',
    ]
    
    list_display_links = ['id', 'customer_link']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Filters
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    list_filter = [
        'status',
        'date',
        'is_onsite',
        BookingStatusFilter,
        DateRangeFilter,
        ('photographer', admin.RelatedOnlyFieldListFilter),
        ('customer', admin.RelatedOnlyFieldListFilter),
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Search
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    search_fields = [
        'id',
        'customer__name',
        'customer__phone',
        'customer__email',
        'photographer__username',
        'photographer__first_name',
        'photographer__last_name',
        'title',
        'notes',
        'location',
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Ordering
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    ordering = ['-date', '-start_time']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Inlines
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # inlines = [PaymentInline]  # لو عندك
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Fieldsets (تقسيم صفحة التفاصيل)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    fieldsets = (
        ('📋 معلومات الحجز الأساسية', {
            'fields': (
                ('customer', 'photographer'),
                ('title', 'package'),
                ('date', 'start_time', 'end_time'),
                ('duration_hours', 'status'),
            ),
            'classes': ('wide',),
        }),
        ('💰 المالية', {
            'fields': (
                ('price', 'deposit'),
                ('remaining_payment', 'total_price'),
            ),
            'classes': ('collapse',),
        }),
        ('📍 الموقع والتفاصيل', {
            'fields': (
                ('location', 'is_onsite'),
                'notes',
            ),
            'classes': ('collapse',),
        }),
        ('⭐ التقييم', {
            'fields': (
                ('rating', 'feedback'),
            ),
            'classes': ('collapse',),
        }),
        ('📅 التواريخ', {
            'fields': (
                ('created_at', 'updated_at'),
                ('confirmed_at', 'cancelled_at', 'completed_at'),
                ('reminder_sent', 'reminder_sent_at'),
            ),
            'classes': ('collapse',),
        }),
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Readonly Fields
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'confirmed_at',
        'cancelled_at',
        'completed_at',
        'remaining_payment',
        'total_price',
        'duration_in_hours',
        'created_by',
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Actions (إجراءات جماعية)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    actions = [
        'confirm_selected',
        'cancel_selected',
        'complete_selected',
        'send_reminder_selected',
        'export_as_csv',
    ]
    
    def confirm_selected(self, request, queryset):
        """تأكيد الحجوزات المحددة"""
        updated = queryset.filter(status__in=['pending', 'confirmed']).update(
            status='confirmed',
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'تم تأكيد {updated} حجز')
    confirm_selected.short_description = 'تأكيد الحجوزات المحددة'
    
    def cancel_selected(self, request, queryset):
        """إلغاء الحجوزات المحددة"""
        updated = queryset.exclude(status='cancelled').update(
            status='cancelled',
            cancelled_at=timezone.now()
        )
        self.message_user(request, f'تم إلغاء {updated} حجز')
    cancel_selected.short_description = 'إلغاء الحجوزات المحددة'
    
    def complete_selected(self, request, queryset):
        """إنهاء الحجوزات المحددة"""
        updated = queryset.filter(status__in=['confirmed', 'in_progress']).update(
            status='done',
            completed_at=timezone.now()
        )
        self.message_user(request, f'تم إنهاء {updated} حجز')
    complete_selected.short_description = 'إنهاء الحجوزات المحددة'
    
    def send_reminder_selected(self, request, queryset):
        """إرسال تذكير للحجوزات المحددة"""
        updated = queryset.update(
            reminder_sent=True,
            reminder_sent_at=timezone.now()
        )
        self.message_user(request, f'تم إرسال تذكير لـ {updated} حجز')
    send_reminder_selected.short_description = 'إرسال تذكير للحجوزات المحددة'
    
    def export_as_csv(self, request, queryset):
        """تصدير الحجوزات كملف CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'العميل', 'المصور', 'التاريخ', 'البداية', 'النهاية',
            'المدة', 'السعر', 'الدفعة', 'الحالة', 'الموقع'
        ])
        
        for booking in queryset:
            writer.writerow([
                booking.id,
                str(booking.customer),
                str(booking.photographer),
                booking.date,
                booking.start_time,
                booking.end_time,
                booking.duration_in_hours,
                booking.price,
                booking.deposit,
                booking.get_status_display(),
                booking.location,
            ])
        
        return response
    export_as_csv.short_description = 'تصدير CSV'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Custom Display Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @admin.display(description='العميل')
    def customer_link(self, obj):
        """رابط للعميل في صفحة التفاصيل"""
        if obj.customer:
            url = reverse('admin:customers_customer_change', args=[obj.customer.id])
            return format_html(
                '<a href="{}" style="font-weight: bold;">{} 📞 {}</a>',
                url,
                obj.customer.name,
                obj.customer.phone if hasattr(obj.customer, 'phone') else ''
            )
        return '-'
    
    @admin.display(description='المصور')
    def photographer_link(self, obj):
        """رابط للمصور في صفحة التفاصيل"""
        if obj.photographer:
            url = reverse('admin:users_user_change', args=[obj.photographer.id])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.photographer.get_full_name() or obj.photographer.username
            )
        return '-'
    
    @admin.display(description='التاريخ')
    def date_display(self, obj):
        """عرض التاريخ بشكل منسق"""
        if obj.date:
            # تحديد لون مختلف للأيام الماضية/الحالية/القادمة
            today = timezone.now().date()
            if obj.date < today:
                color = '#dc3545'  # أحمر - منتهي
            elif obj.date == today:
                color = '#28a745'  # أخضر - اليوم
            else:
                color = '#007bff'  # أزرق - قادم
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                obj.date.strftime('%Y-%m-%d')
            )
        return '-'
    
    @admin.display(description='الوقت')
    def time_display(self, obj):
        """عرض الوقت بشكل منسق"""
        return format_html(
            '{} → {} <span style="font-size: 0.8em; color: #6c757d;">({} ساعة)</span>',
            obj.start_time.strftime('%I:%M %p'),
            obj.end_time.strftime('%I:%M %p'),
            obj.duration_in_hours
        )
    
    @admin.display(description='المدة')
    def duration_badge(self, obj):
        """عرض المدة كـ Badge"""
        hours = obj.duration_in_hours
        if hours <= 1:
            color = '#28a745'  # أخضر
        elif hours <= 3:
            color = '#ffc107'  # أصفر
        else:
            color = '#dc3545'  # أحمر
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">{} ساعة</span>',
            color,
            hours
        )
    
    @admin.display(description='الحالة')
    def status_badge(self, obj):
        """عرض الحالة كـ Badge ملونة"""
        status_colors = {
            'pending': '#ffc107',      # أصفر
            'confirmed': '#17a2b8',    # أزرق
            'in_progress': '#007bff',  # أزرق غامق
            'done': '#28a745',         # أخضر
            'cancelled': '#dc3545',    # أحمر
            'no_show': '#6c757d',      # رمادي
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 12px; border-radius: 12px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_status_display()
        )
    
    @admin.display(description='السعر')
    def price_display(self, obj):
        """عرض السعر مع الدفعة"""
        if obj.price:
            if obj.deposit:
                return format_html(
                    '💰 {} <span style="color: #6c757d; font-size: 0.8em;">(دفعة: {})</span>',
                    obj.price,
                    obj.deposit
                )
            return format_html('💰 {}', obj.price)
        return '-'
    
    @admin.display(description='أنشئ منذ')
    def created_ago(self, obj):
        """عرض وقت الإنشاء بشكل نسبي"""
        from django.utils.timesince import timesince
        return timesince(obj.created_at)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Stats in Admin (إحصائيات في أعلى الصفحة)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def changelist_view(self, request, extra_context=None):
        """إضافة إحصائيات إلى صفحة القائمة"""
        extra_context = extra_context or {}
        
        # إحصائيات عامة
        total = Booking.objects.count()
        pending = Booking.objects.filter(status='pending').count()
        confirmed = Booking.objects.filter(status='confirmed').count()
        done = Booking.objects.filter(status='done').count()
        cancelled = Booking.objects.filter(status='cancelled').count()
        
        # إيرادات الشهر الحالي
        today = timezone.now()
        monthly_revenue = Booking.objects.filter(
            status='done',
            date__year=today.year,
            date__month=today.month
        ).aggregate(total=Sum('price'))['total'] or 0
        
        extra_context['stats'] = {
            'total': total,
            'pending': pending,
            'confirmed': confirmed,
            'done': done,
            'cancelled': cancelled,
            'monthly_revenue': monthly_revenue,
        }
        
        return super().changelist_view(request, extra_context=extra_context)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Save & Delete Overrides
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def save_model(self, request, obj, form, change):
        """تعيين من قام بالإنشاء عند الحفظ"""
        if not change:  # إنشاء جديد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """تسجيل من قام بالحذف (اختياري)"""
        # يمكنك تسجيل عملية الحذف في Log
        super().delete_model(request, obj)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Permission Overrides (صلاحيات مخصصة)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def has_delete_permission(self, request, obj=None):
        """فقط الأدمن يمكنهم الحذف"""
        if request.user.is_superuser:
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        """الموظفون يمكنهم التعديل"""
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 Admin Template Override (لو عاوز تعديل الـ Template)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# لو عاوز تضيف stats في أعلى الصفحة، اعمل ملف:
# templates/admin/reports_app/booking/change_list.html
# 
# {% extends "admin/change_list.html" %}
# {% block content %}
# <div class="stats-container" style="display: flex; gap: 20px; margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
#     <div><strong>إجمالي الحجوزات:</strong> {{ stats.total }}</div>
#     <div><strong>قيد الانتظار:</strong> {{ stats.pending }}</div>
#     <div><strong>مؤكد:</strong> {{ stats.confirmed }}</div>
#     <div><strong>منتهي:</strong> {{ stats.done }}</div>
#     <div><strong>ملغي:</strong> {{ stats.cancelled }}</div>
#     <div><strong>إيرادات الشهر:</strong> {{ stats.monthly_revenue }}</div>
# </div>
# {{ block.super }}
# {% endblock %}