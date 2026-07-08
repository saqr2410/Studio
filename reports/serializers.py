from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Report, ReportTemplate, ReportSchedule

User = get_user_model()


class ReportListSerializer(serializers.ModelSerializer):
    """Serializers لعرض التقارير (خفيف)"""
    
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'report_type_display',
            'format', 'format_display', 'status', 'status_display',
            'start_date', 'end_date', 'generated_at',
            'created_by', 'created_by_name',
            'file_url', 'is_completed',
        ]


class ReportDetailSerializer(serializers.ModelSerializer):
    """Serializers لعرض تفاصيل التقرير (كامل)"""
    
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    duration_days = serializers.ReadOnlyField()
    file_size = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'report_type_display',
            'format', 'format_display', 'status', 'status_display',
            'start_date', 'end_date', 'duration_days',
            'filters', 'data', 'summary',
            'file', 'file_url', 'file_size',
            'notes',
            'generated_at', 'completed_at', 'updated_at',
            'created_by', 'created_by_name',
            'is_completed',
        ]
        read_only_fields = ['generated_at', 'completed_at', 'updated_at', 'data']


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializers لإنشاء تقرير"""
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'format',
            'start_date', 'end_date', 'filters', 'notes',
        ]
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': 'تاريخ النهاية يجب أن يكون بعد تاريخ البداية'
            })
        
        return data


class ReportUpdateSerializer(serializers.ModelSerializer):
    """Serializers لتحديث التقرير"""
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'notes', 'status',
        ]


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializers لقوالب التقارير"""
    
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'report_type', 'report_type_display',
            'description', 'config', 'is_default', 'is_active',
            'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializers لجداول التقارير"""
    
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    report_title = serializers.CharField(source='report.title', read_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'report', 'report_title',
            'frequency', 'frequency_display',
            'day_of_week', 'day_of_month', 'time',
            'recipients', 'is_active',
            'last_run', 'next_run',
            'created_at', 'updated_at',
        ]


class ReportSummarySerializer(serializers.Serializer):
    """Serializers لملخص التقارير"""
    
    total_reports = serializers.IntegerField()
    by_type = serializers.DictField()
    by_status = serializers.DictField()
    by_format = serializers.DictField()
    recent = ReportListSerializer(many=True)


class ReportDataSerializer(serializers.Serializer):
    """Serializers لبيانات التقرير المتخصصة"""
    
    # تقرير الحجوزات
    total_bookings = serializers.IntegerField(required=False)
    confirmed = serializers.IntegerField(required=False)
    pending = serializers.IntegerField(required=False)
    cancelled = serializers.IntegerField(required=False)
    done = serializers.IntegerField(required=False)
    
    # تقرير مالي
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    
    # تقرير العملاء
    total_customers = serializers.IntegerField(required=False)
    new_customers = serializers.IntegerField(required=False)
    vip_customers = serializers.IntegerField(required=False)
    
    # تقرير المصورين
    total_photographers = serializers.IntegerField(required=False)
    active_photographers = serializers.IntegerField(required=False)
    
    # البيانات التفصيلية
    details = serializers.ListField(required=False)
    chart_data = serializers.DictField(required=False)