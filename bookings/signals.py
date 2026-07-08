from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Booking
from django.utils import timezone


@receiver(pre_save, sender=Booking)
def booking_pre_save(sender, instance, **kwargs):
    """تنفيذ إجراءات قبل الحفظ"""
    # حساب المدة تلقائياً
    if not instance.duration_hours:
        start = timezone.datetime.combine(instance.date, instance.start_time)
        end = timezone.datetime.combine(instance.date, instance.end_time)
        instance.duration_hours = round((end - start).total_seconds() / 3600, 1)

@receiver(post_save, sender=Booking)
def booking_post_save(sender, instance, created, **kwargs):
    """تنفيذ إجراءات بعد الحفظ"""
    if created:
        # إرسال إشعار للعميل
        pass
    elif instance.status == 'confirmed' and not instance.confirmed_at:
        # إرسال تأكيد
        pass