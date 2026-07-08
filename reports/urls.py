from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, ReportTemplateViewSet, ReportScheduleViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='reports')
router.register(r'templates', ReportTemplateViewSet, basename='templates')
router.register(r'schedules', ReportScheduleViewSet, basename='schedules')

urlpatterns = [
    path('', include(router.urls)),
]