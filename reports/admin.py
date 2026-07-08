from django.contrib import admin
from django.utils.html import format_html
from .models import Report, ReportTemplate, ReportSchedule


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'report_type_badge', 'format_badge',
        'status_badge', 'generated_at', 'created_by'
    ]
    list_filter = ['report_type', 'status', 'format', 'generated_at']
    search_fields = ['title', 'notes']
    readonly_fields = ['data', 'summary', 'generated_at', 'completed_at']
    
    def report_type_badge(self, obj):
        return format_html(
            '<span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 4px;">{}</span>',
            obj.get_report_type_display()
        )
    report_type_badge.short_description = 'النوع'
    
    def format_badge(self, obj):
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 4px;">{}</span>',
            obj.get_format_display()
        )
    format_badge.short_description = 'الصيغة'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 4px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'الحالة'


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_default', 'is_active', 'created_at']
    list_filter = ['report_type', 'is_default', 'is_active']
    search_fields = ['name', 'description']


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ['report', 'frequency', 'is_active', 'next_run', 'last_run']
    list_filter = ['frequency', 'is_active']
    search_fields = ['report__title']