from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    إدارة المستخدمين في Django Admin
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 List Display
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    list_display = [
        'id',
        'username_link',
        'full_name',
        'email',
        'phone_short',
        'role_badge',
        'status_badge',
        'is_active_badge',
        'is_verified_badge',
        'last_active_ago',
    ]
    
    list_display_links = ['id', 'username_link']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Filters
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    list_filter = [
        'role',
        'status',
        'is_active',
        'is_verified',
        'gender',
        ('created_at', admin.DateFieldListFilter),
        ('last_active', admin.DateFieldListFilter),
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Search
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    search_fields = [
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'phone',
        'address',
        'city',
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Ordering
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    ordering = ['-created_at']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Fieldsets
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    fieldsets = (
        ('👤 معلومات الحساب', {
            'fields': (
                ('username', 'email'),
                ('password',),
                ('first_name', 'last_name'),
            ),
        }),
        ('📞 معلومات الاتصال', {
            'fields': (
                ('phone', 'gender'),
                ('date_of_birth',),
                ('address', 'city', 'country'),
            ),
        }),
        ('📸 الصورة الشخصية', {
            'fields': ('profile_picture', 'bio'),
            'classes': ('collapse',),
        }),
        ('🏢 الدور والحالة', {
            'fields': (
                ('role', 'status'),
                ('is_active', 'is_verified'),
                ('hire_date',),
            ),
        }),
        ('🎯 المهارات والتخصصات', {
            'fields': (
                'skills',
                'specialties',
            ),
            'classes': ('collapse',),
        }),
        ('⚙️ الإعدادات', {
            'fields': (
                ('theme_preference', 'language', 'timezone'),
                'notification_preferences',
            ),
            'classes': ('collapse',),
        }),
        ('📊 إحصائيات', {
            'fields': ('last_active',),
            'classes': ('collapse',),
        }),
        ('📅 التواريخ الإدارية', {
            'fields': (
                ('created_at', 'updated_at'),
                'created_by',
            ),
            'classes': ('collapse',),
        }),
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Add Fieldsets
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'role', 'status', 'is_active',
            ),
        }),
        ('معلومات إضافية', {
            'classes': ('collapse',),
            'fields': (
                'first_name', 'last_name', 'phone',
                'gender', 'date_of_birth',
            ),
        }),
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Readonly Fields
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    readonly_fields = ['created_at', 'updated_at', 'last_active', 'created_by']
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    actions = [
        'activate_selected',
        'deactivate_selected',
        'make_admin',
        'make_receptionist',
        'make_photographer',
        'make_manager',
        'make_accountant',
        'export_as_csv',
    ]
    
    def activate_selected(self, request, queryset):
        """تفعيل المستخدمين المحددين"""
        updated = queryset.update(is_active=True, status=User.Status.ACTIVE)
        self.message_user(request, f'تم تفعيل {updated} مستخدم')
    activate_selected.short_description = 'تفعيل المستخدمين المحددين ✅'
    
    def deactivate_selected(self, request, queryset):
        """تعطيل المستخدمين المحددين"""
        # منع تعطيل آخر مدير
        admin_queryset = queryset.filter(role=User.Roles.ADMIN)
        if admin_queryset.exists():
            admin_count = User.objects.filter(role=User.Roles.ADMIN).count()
            if admin_count <= admin_queryset.count():
                self.message_user(
                    request,
                    'لا يمكن تعطيل آخر مدير في النظام',
                    level='ERROR'
                )
                return
        
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم تعطيل {updated} مستخدم')
    deactivate_selected.short_description = 'تعطيل المستخدمين المحددين ⛔'
    
    def make_admin(self, request, queryset):
        """ترقية المستخدمين إلى مدير"""
        updated = queryset.update(role=User.Roles.ADMIN)
        self.message_user(request, f'تم ترقية {updated} مستخدم إلى مدير')
    make_admin.short_description = 'ترقية إلى مدير 👑'
    
    def make_receptionist(self, request, queryset):
        """تحويل المستخدمين إلى موظف استقبال"""
        updated = queryset.update(role=User.Roles.RECEPTIONIST)
        self.message_user(request, f'تم تحويل {updated} مستخدم إلى موظف استقبال')
    make_receptionist.short_description = 'تحويل إلى موظف استقبال 📞'
    
    def make_photographer(self, request, queryset):
        """تحويل المستخدمين إلى مصور"""
        updated = queryset.update(role=User.Roles.PHOTOGRAPHER)
        self.message_user(request, f'تم تحويل {updated} مستخدم إلى مصور')
    make_photographer.short_description = 'تحويل إلى مصور 📸'
    
    def make_manager(self, request, queryset):
        """تحويل المستخدمين إلى مدير فرع"""
        updated = queryset.update(role=User.Roles.MANAGER)
        self.message_user(request, f'تم تحويل {updated} مستخدم إلى مدير فرع')
    make_manager.short_description = 'تحويل إلى مدير فرع 🏢'
    
    def make_accountant(self, request, queryset):
        """تحويل المستخدمين إلى محاسب"""
        updated = queryset.update(role=User.Roles.ACCOUNTANT)
        self.message_user(request, f'تم تحويل {updated} مستخدم إلى محاسب')
    make_accountant.short_description = 'تحويل إلى محاسب 💰'
    
    def export_as_csv(self, request, queryset):
        """تصدير المستخدمين كملف CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'اسم المستخدم', 'البريد', 'الدور', 'الحالة', 'نشط', 'تاريخ الإنشاء'
        ])
        
        for user in queryset:
            writer.writerow([
                user.id,
                user.get_full_name() or user.username,
                user.email,
                user.get_role_display(),
                user.get_status_display(),
                'نعم' if user.is_active else 'لا',
                user.created_at.strftime('%Y-%m-%d'),
            ])
        
        return response
    export_as_csv.short_description = 'تصدير CSV 📄'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Custom Display Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @admin.display(description='المستخدم')
    def username_link(self, obj):
        """رابط للمستخدم"""
        url = reverse('admin:users_user_change', args=[obj.id])
        return format_html(
            '<a href="{}"><strong>@{}</strong></a>',
            url,
            obj.username
        )
    
    @admin.display(description='الاسم الكامل')
    def full_name(self, obj):
        """الاسم الكامل"""
        return obj.get_full_name() or '-'
    
    @admin.display(description='الهاتف')
    def phone_short(self, obj):
        """عرض الهاتف مختصراً"""
        if obj.phone:
            if len(obj.phone) > 12:
                return f"{obj.phone[:6]}...{obj.phone[-4:]}"
            return obj.phone
        return '-'
    
    @admin.display(description='الدور')
    def role_badge(self, obj):
        """عرض الدور كـ Badge"""
        colors = {
            User.Roles.ADMIN: '#dc3545',
            User.Roles.MANAGER: '#fd7e14',
            User.Roles.RECEPTIONIST: '#007bff',
            User.Roles.PHOTOGRAPHER: '#28a745',
            User.Roles.ACCOUNTANT: '#6f42c1',
            User.Roles.ASSISTANT: '#6c757d',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 12px; border-radius: 12px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_role_display()
        )
    
    @admin.display(description='الحالة')
    def status_badge(self, obj):
        """عرض الحالة كـ Badge"""
        colors = {
            User.Status.ACTIVE: '#28a745',
            User.Status.INACTIVE: '#6c757d',
            User.Status.SUSPENDED: '#dc3545',
            User.Status.ON_LEAVE: '#ffc107',
        }
        color = colors.get(obj.status, '#6c757d')
        icons = {
            User.Status.ACTIVE: '✅',
            User.Status.INACTIVE: '⛔',
            User.Status.SUSPENDED: '🚫',
            User.Status.ON_LEAVE: '🏖️',
        }
        icon = icons.get(obj.status, '')
        return format_html(
            '<span style="background: {}; color: {}; padding: 2px 12px; border-radius: 12px; font-size: 0.85em;">{} {}</span>',
            color,
            '#000' if obj.status == User.Status.ON_LEAVE else '#fff',
            icon,
            obj.get_status_display()
        )
    
    @admin.display(description='نشط')
    def is_active_badge(self, obj):
        """عرض حالة النشاط"""
        if obj.is_active:
            return format_html('✅ نعم')
        return format_html('❌ لا')
    
    @admin.display(description='موثق')
    def is_verified_badge(self, obj):
        """عرض حالة التوثيق"""
        if obj.is_verified:
            return format_html('✅ نعم')
        return format_html('❌ لا')
    
    @admin.display(description='آخر نشاط')
    def last_active_ago(self, obj):
        """عرض آخر نشاط بشكل نسبي"""
        if obj.last_active:
            from django.utils.timesince import timesince
            return timesince(obj.last_active)
        return 'لم يسبق'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Stats in Admin
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def changelist_view(self, request, extra_context=None):
        """إضافة إحصائيات إلى صفحة القائمة"""
        extra_context = extra_context or {}
        
        extra_context['stats'] = {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True, status=User.Status.ACTIVE).count(),
            'admin': User.objects.filter(role=User.Roles.ADMIN, is_active=True).count(),
            'photographers': User.objects.filter(role=User.Roles.PHOTOGRAPHER, is_active=True).count(),
            'receptionists': User.objects.filter(role=User.Roles.RECEPTIONIST, is_active=True).count(),
        }
        
        return super().changelist_view(request, extra_context=extra_context)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Save
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)