from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from finance.models import Income


@receiver(post_save, sender=Payment)
def create_income_from_payment(sender, instance, created, **kwargs):
    """إنشاء إيراد عند تأكيد الدفعة"""
    if instance.status == Payment.Status.PAID:
        # خلي الإيراد يتضيف بس لو مش موجود
        Income.objects.get_or_create(
            booking=instance.booking,
            amount=instance.amount,
            source=Income.Source.BOOKING,
            defaults={
                'title': f'دفعة من حجز #{instance.booking.id}',
                'payment_method': instance.payment_method,
                'customer': instance.booking.customer,
                'income_date': instance.payment_date,
                'description': f'دفعة #{instance.id}',
            }
        )