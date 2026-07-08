from django.db import models


class Package(models.Model):
    """
    باقة خدمات (تصوير / مناسبات / إلخ)
    """

    class Category(models.TextChoices):
        WEDDING = 'wedding', 'زفاف'
        BIRTHDAY = 'birthday', 'عيد ميلاد'
        EVENT = 'event', 'مناسبات'
        STUDIO = 'studio', 'استوديو'

    name = models.CharField(
        max_length=255,
        verbose_name="اسم الباقة"
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        verbose_name="نوع الباقة"
    )

    description = models.TextField(
        blank=True,
        verbose_name="الوصف"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="السعر"
    )

    duration_hours = models.PositiveIntegerField(
        default=1,
        verbose_name="عدد الساعات"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="نشطة"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "باقة"
        verbose_name_plural = "الباقات"

    def __str__(self):
        return f"{self.name} - {self.price}"