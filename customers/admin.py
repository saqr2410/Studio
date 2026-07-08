from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from django.contrib.admin import SimpleListFilter
from .models import Customer


class CustomerTypeFilter(SimpleListFilter):
    """فلتر مخصص لنوع العميل"""
    title = 'نوع العميل'
    parameter_name = 'customer_type'
    
    def lookups(self, request, model_admin):
        return (
            ('vip', 'VIP ⭐'),
            ('regular', 'عادي'),
            ('corporate', 'شركة'),
            ('agency', 'وكالة'),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(customer_type=self.value())
        return queryset


class CustomerStatusFilter(SimpleListFilter):
    """فلتر مخصص لحالة العميل"""
    title = 'الحالة'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return (
            ('active', 'نشط'),
            ('inactive', 'غير نشط'),
            ('blacklisted', 'محظور'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True, is_blacklisted=False)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)
        if self.value() == 'blacklisted':
            return queryset.filter(is_blacklisted=True)
        return queryset


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    إدارة احترافية للعملاء في Django Admin
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 List Display
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    list_display = [
        'id',
        'name_link',
        'phone_display',
        'email',
        'customer_type_badge',
        'status_badge',
        'total_bookings',
        'total_spent_display',
        'created_at_display',
    ]
    
    list_display_links = ['id', 'name_link']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Filters
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    list_filter = [
        CustomerTypeFilter,
        CustomerStatusFilter,
        'gender',
        'is_active',
        'is_blacklisted',
        ('created_at', admin.DateFieldListFilter),
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Search
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    search_fields = [
        'id',
        'name',
        'phone',
        'email',
        'address',
        'notes',
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Ordering
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    ordering = ['-created_at']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Fieldsets
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    fieldsets = (
        ('👤 المعلومات الأساسية', {
            'fields': (
                ('name', 'phone'),
                ('email', 'gender'),
                ('customer_type', 'date_of_birth'),
            ),
        }),
        ('📍 العنوان', {
            'fields': (
                ('address', 'city', 'country'),
            ),
            'classes': ('collapse',),
        }),
        ('🌐 وسائل التواصل', {
            'fields': (
                ('instagram', 'facebook'),
                ('twitter', 'website'),
            ),
            'classes': ('collapse',),
        }),
        ('⭐ التفضيلات', {
            'fields': (
                ('preferred_photographer', 'preferred_package'),
                'preferred_contact_method',
            ),
            'classes': ('collapse',),
        }),
        ('📝 ملاحظات وإعدادات', {
            'fields': (
                'notes',
                ('is_active', 'is_blacklisted'),
                'blacklist_reason',
            ),
        }),
        ('📊 الإحصائيات', {
            'fields': (
                ('total_bookings', 'total_spent'),
                'last_booking_date',
            ),
            'classes': ('collapse',),
        }),
        ('📅 التواريخ', {
            'fields': (
                ('created_at', 'updated_at'),
                'created_by',
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
        'total_bookings',
        'total_spent',
        'last_booking_date',
        'created_by',
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    actions = [
        'make_active',
        'make_inactive',
        'make_vip',
        'make_regular',
        'export_as_csv',
        'send_bulk_email',
    ]
    
    def make_active(self, request, queryset):
        """تفعيل العملاء المحددين"""
        updated = queryset.update(is_active=True, is_blacklisted=False, blacklist_reason='')
        self.message_user(request, f'تم تفعيل {updated} عميل')
    make_active.short_description = 'تفعيل العملاء المحددين'
    
    def make_inactive(self, request, queryset):
        """تعطيل العملاء المحددين"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم تعطيل {updated} عميل')
    make_inactive.short_description = 'تعطيل العملاء المحددين'
    
    def make_vip(self, request, queryset):
        """ترقية العملاء إلى VIP"""
        updated = queryset.update(customer_type=Customer.TYPE_VIP)
        self.message_user(request, f'تم ترقية {updated} عميل إلى VIP')
    make_vip.short_description = 'ترقية إلى VIP ⭐'
    
    def make_regular(self, request, queryset):
        """تحويل العملاء إلى عادي"""
        updated = queryset.update(customer_type=Customer.TYPE_REGULAR)
        self.message_user(request, f'تم تحويل {updated} عميل إلى عادي')
    make_regular.short_description = 'تحويل إلى عادي'
    
    def export_as_csv(self, request, queryset):
        """تصدير العملاء كملف CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'الاسم', 'الهاتف', 'البريد', 'النوع',
            'الحالة', 'عدد الحجوزات', 'إجمالي المصروفات'
        ])
        
        for customer in queryset:
            writer.writerow([
                customer.id,
                customer.name,
                customer.phone,
                customer.email or '',
                customer.get_customer_type_display(),
                customer.status_badge,
                customer.total_bookings,
                customer.total_spent,
            ])
        
        return response
    export_as_csv.short_description = 'تصدير CSV'
    
    def send_bulk_email(self, request, queryset):
        """إرسال بريد جماعي للعملاء المحددين"""
        emails = [c.email for c in queryset if c.email]
        if emails:
            self.message_user(
                request,
                f'تم إرسال البريد لـ {len(emails)} عميل (محاكاة)'
            )
        else:
            self.message_user(
                request,
                'لا يوجد بريد إلكتروني للعملاء المحددين',
                level='ERROR'
            )
    send_bulk_email.short_description = 'إرسال بريد جماعي (محاكاة)'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Custom Display Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @admin.display(description='الاسم')
    def name_link(self, obj):
        """رابط للعميل"""
        if obj.pk:
            url = reverse('admin:customers_customer_change', args=[obj.pk])
            return format_html('<a href="{}"><strong>{}</strong></a>', url, obj.name)
        return obj.name
    
    @admin.display(description='الهاتف')
    def phone_display(self, obj):
        """عرض الهاتف بشكل منسق"""
        if obj.phone:
            return format_html(
                '<span style="direction: ltr; unicode-bidi: embed;">📞 {}</span>',
                obj.phone
            )
        return '-'
    
    @admin.display(description='النوع')
    def customer_type_badge(self, obj):
        """عرض نوع العميل كـ Badge"""
        colors = {
            Customer.TYPE_VIP: '#FFD700',
            Customer.TYPE_REGULAR: '#6c757d',
            Customer.TYPE_CORPORATE: '#007bff',
            Customer.TYPE_AGENCY: '#17a2b8',
        }
        color = colors.get(obj.customer_type, '#6c757d')
        return format_html(
            '<span style="background: {}; color: {}; padding: 2px 10px; border-radius: 12px; font-size: 0.85em;">{}</span>',
            color,
            '#000' if obj.customer_type == Customer.TYPE_VIP else '#fff',
            obj.get_customer_type_display()
        )
    
    @admin.display(description='الحالة')
    def status_badge(self, obj):
        """عرض الحالة كـ Badge"""
        if obj.is_blacklisted:
            color = '#dc3545'
            status = 'محظور ⛔'
        elif not obj.is_active:
            color = '#6c757d'
            status = 'غير نشط'
        elif obj.is_vip:
            color = '#FFD700'
            status = 'VIP ⭐'
        else:
            color = '#28a745'
            status = 'نشط ✅'
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 2px 12px; border-radius: 12px; font-size: 0.85em;">{}</span>',
            color,
            '#000' if obj.is_vip or color == '#FFD700' else '#fff',
            status
        )
    
    @admin.display(description='المصروفات')
    def total_spent_display(self, obj):
        """عرض المصروفات بشكل منسق"""
        if obj.total_spent:
            return format_html(
                '<span style="font-weight: bold; color: #28a745;">💰 {:.2f}</span>',
                obj.total_spent
            )
        return '-'
    
    @admin.display(description='تاريخ الإنشاء')
    def created_at_display(self, obj):
        """عرض تاريخ الإنشاء بشكل منسق"""
        from django.utils.timesince import timesince
        return format_html(
            '<span title="{}">{}</span>',
            obj.created_at.strftime('%Y-%m-%d %H:%M'),
            timesince(obj.created_at)
        )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Stats
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def changelist_view(self, request, extra_context=None):
        """إضافة إحصائيات إلى صفحة القائمة"""
        extra_context = extra_context or {}
        
        extra_context['stats'] = {
            'total': Customer.objects.count(),
            'active': Customer.objects.filter(is_active=True, is_blacklisted=False).count(),
            'vip': Customer.objects.filter(customer_type=Customer.TYPE_VIP, is_active=True).count(),
            'blacklisted': Customer.objects.filter(is_blacklisted=True).count(),
            'total_revenue': Customer.objects.aggregate(total=Sum('total_spent'))['total'] or 0,
        }
        
        return super().changelist_view(request, extra_context=extra_context)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Save
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)