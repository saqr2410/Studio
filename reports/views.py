from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Q
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Report, ReportTemplate, ReportSchedule
from .serializers import (
    ReportListSerializer,
    ReportDetailSerializer,
    ReportCreateSerializer,
    ReportUpdateSerializer,
    ReportTemplateSerializer,
    ReportScheduleSerializer,
    ReportSummarySerializer,
    ReportDataSerializer,
)
from .utils import ReportGenerator
from .tasks import generate_report_task
from users.permissions import IsAdmin, IsReceptionistOrAdmin


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة التقارير
    """
    
    queryset = Report.objects.select_related('created_by').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'notes', 'data']
    ordering_fields = ['generated_at', 'title', 'status']
    ordering = ['-generated_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReportListSerializer
        elif self.action == 'create':
            return ReportCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReportUpdateSerializer
        elif self.action == 'retrieve':
            return ReportDetailSerializer
        elif self.action == 'summary':
            return ReportSummarySerializer
        return ReportDetailSerializer
    
    def get_permissions(self):
        permissions_map = {
            'list': [IsReceptionistOrAdmin],
            'retrieve': [IsReceptionistOrAdmin],
            'create': [IsReceptionistOrAdmin],
            'update': [IsAdmin],
            'partial_update': [IsAdmin],
            'destroy': [IsAdmin],
            'summary': [IsAdmin],
            'generate': [IsReceptionistOrAdmin],
            'download': [IsReceptionistOrAdmin],
            'regenerate': [IsAdmin],
            'schedule': [IsAdmin],
        }
        permission_classes = permissions_map.get(self.action, [IsAdmin])
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        report = serializer.save(created_by=self.request.user)
        # تشغيل التوليد في الخلفية
        generate_report_task.delay(report.id)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Custom Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """توليد التقرير"""
        report = self.get_object()
        
        if report.is_processing:
            return Response(
                {'error': 'التقرير قيد التوليد حالياً'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # تشغيل التوليد
        generate_report_task.delay(report.id)
        
        return Response({
            'message': 'بدأ توليد التقرير',
            'report_id': report.id
        })
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """تحميل ملف التقرير"""
        report = self.get_object()
        
        if not report.is_completed:
            return Response(
                {'error': 'التقرير غير مكتمل بعد'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not report.file:
            return Response(
                {'error': 'لا يوجد ملف للتقرير'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from django.http import FileResponse
        return FileResponse(report.file, as_attachment=True)
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """إعادة توليد التقرير"""
        report = self.get_object()
        
        # حذف الملف القديم
        if report.file:
            report.file.delete()
        
        # إعادة تعيين الحالة
        report.status = Report.Status.PENDING
        report.completed_at = None
        report.data = {}
        report.summary = {}
        report.file = None
        report.save()
        
        # إعادة التوليد
        generate_report_task.delay(report.id)
        
        return Response({
            'message': 'جاري إعادة توليد التقرير',
            'report_id': report.id
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """ملخص التقارير"""
        # إحصائيات عامة
        total = Report.objects.count()
        
        by_type = dict(
            Report.objects.values('report_type').annotate(
                count=Count('id')
            ).values_list('report_type', 'count')
        )
        
        by_status = dict(
            Report.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        )
        
        by_format = dict(
            Report.objects.values('format').annotate(
                count=Count('id')
            ).values_list('format', 'count')
        )
        
        recent = Report.objects.select_related('created_by')[:10]
        
        data = {
            'total_reports': total,
            'by_type': by_type,
            'by_status': by_status,
            'by_format': by_format,
            'recent': ReportListSerializer(recent, many=True).data,
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """تقارير المستخدم الحالي"""
        reports = self.get_queryset().filter(created_by=request.user)
        page = self.paginate_queryset(reports)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate_from_template(self, request):
        """توليد تقرير من قالب"""
        template_id = request.data.get('template_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not template_id:
            return Response(
                {'error': 'يجب إرسال template_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        template = get_object_or_404(ReportTemplate, id=template_id, is_active=True)
        
        # إنشاء التقرير من القالب
        report = Report.objects.create(
            title=f"{template.name} - {timezone.now().strftime('%Y-%m-%d')}",
            report_type=template.report_type,
            filters=template.config.get('filters', {}),
            created_by=request.user,
            start_date=start_date,
            end_date=end_date,
        )
        
        # توليد التقرير
        generate_report_task.delay(report.id)
        
        return Response({
            'message': 'تم بدء توليد التقرير من القالب',
            'report_id': report.id
        })
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """التقارير حسب النوع"""
        report_type = request.query_params.get('type')
        if not report_type:
            return Response(
                {'error': 'يجب إرسال type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reports = self.get_queryset().filter(report_type=report_type)
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """التقارير حسب النطاق الزمني"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(generated_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(generated_at__date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet لإدارة قوالب التقارير"""
    
    queryset = ReportTemplate.objects.select_related('created_by').all()
    serializer_class = ReportTemplateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['-is_default', 'name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsReceptionistOrAdmin()]
        return [IsAdmin()]
    
    def perform_create(self, serializer):
        # إذا كان القالب افتراضي، إزالة الافتراضي من القوالب الأخرى
        if serializer.validated_data.get('is_default'):
            ReportTemplate.objects.filter(
                report_type=serializer.validated_data.get('report_type'),
                is_default=True
            ).update(is_default=False)
        
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        # إذا كان القالب افتراضي، إزالة الافتراضي من القوالب الأخرى
        if serializer.validated_data.get('is_default'):
            ReportTemplate.objects.filter(
                report_type=serializer.validated_data.get('report_type'),
                is_default=True
            ).exclude(id=self.get_object().id).update(is_default=False)
        
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """القوالب حسب النوع"""
        report_type = request.query_params.get('type')
        if not report_type:
            return Response(
                {'error': 'يجب إرسال type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        templates = self.get_queryset().filter(
            report_type=report_type,
            is_active=True
        )
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """القوالب الافتراضية"""
        templates = self.get_queryset().filter(is_default=True, is_active=True)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet لإدارة جداول التقارير"""
    
    queryset = ReportSchedule.objects.select_related('report').all()
    serializer_class = ReportScheduleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['report__title']
    ordering = ['next_run']
    
    def get_permissions(self):
        return [IsAdmin()]
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """تشغيل الجدول الآن"""
        schedule = self.get_object()
        
        # توليد التقرير
        generate_report_task.delay(schedule.report.id)
        
        # تحديث آخر تشغيل
        schedule.last_run = timezone.now()
        schedule.save()
        
        return Response({
            'message': 'تم تشغيل الجدول بنجاح',
            'schedule_id': schedule.id
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """الجداول النشطة"""
        schedules = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)