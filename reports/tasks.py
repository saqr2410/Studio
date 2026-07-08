from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .utils import ReportGenerator


@shared_task(bind=True)
def generate_report_task(self, report_id):
    """توليد التقرير في الخلفية"""
    from .models import Report
    
    try:
        generator = ReportGenerator(report_id)
        generator.generate()
        
        # إرسال إشعار
        report = Report.objects.get(id=report_id)
        if report.created_by and report.created_by.email:
            send_mail(
                subject=f"اكتمل تقريرك: {report.title}",
                message=f"تم توليد التقرير بنجاح. يمكنك تحميله من لوحة التحكم.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[report.created_by.email],
            )
        
        return {"status": "success", "report_id": report_id}
        
    except Exception as e:
        # تحديث حالة التقرير بالفشل
        from .models import Report
        report = Report.objects.get(id=report_id)
        report.mark_failed(str(e))
        return {"status": "failed", "error": str(e)}


@shared_task
def generate_scheduled_report(schedule_id):
    """توليد تقرير مجدول"""
    from .models import ReportSchedule
    
    schedule = ReportSchedule.objects.get(id=schedule_id)
    generate_report_task.delay(schedule.report.id)


@shared_task
def cleanup_old_reports():
    """تنظيف التقارير القديمة"""
    from .models import Report
    import datetime
    
    # حذف التقارير الأقدم من 30 يوماً
    cutoff = datetime.datetime.now() - datetime.timedelta(days=30)
    old_reports = Report.objects.filter(
        created_at__lt=cutoff,
        status='completed'
    )
    
    for report in old_reports:
        if report.file:
            report.file.delete()
        report.delete()