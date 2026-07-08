from rest_framework import serializers
from django.utils import timezone
from .models import Payment
from django.db import models

class PaymentListSerializer(serializers.ModelSerializer):
    """Serializers لعرض المدفوعات (خفيف)"""
    
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    customer_name = serializers.ReadOnlyField()
    booking_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'amount', 'payment_type', 'payment_type_display',
            'status', 'status_display', 'payment_method', 'payment_method_display',
            'payment_date', 'created_at', 'customer_name', 'booking_amount',
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Serializers لعرض تفاصيل الدفعة (كامل)"""
    
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    customer_name = serializers.ReadOnlyField()
    photographer_name = serializers.ReadOnlyField()
    booking_amount = serializers.ReadOnlyField()
    total_paid_for_booking = serializers.ReadOnlyField()
    remaining_balance = serializers.ReadOnlyField()
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    booking_details = serializers.SerializerMethodField()
    
    is_paid = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()
    is_failed = serializers.ReadOnlyField()
    is_refunded = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'booking_details',
            'created_by', 'created_by_name',
            'amount', 'payment_type', 'payment_type_display',
            'status', 'status_display',
            'payment_method', 'payment_method_display',
            'reference_number', 'transaction_id',
            'description', 'receipt',
            'payment_date', 'due_date',
            'confirmed_at', 'refunded_at',
            'created_at', 'updated_at',
            'customer_name', 'photographer_name',
            'booking_amount', 'total_paid_for_booking', 'remaining_balance',
            'is_paid', 'is_pending', 'is_failed', 'is_refunded', 'is_overdue',
        ]
        read_only_fields = ['created_at', 'updated_at', 'confirmed_at', 'refunded_at']
    
    def get_booking_details(self, obj):
        """تفاصيل الحجز المرتبط"""
        from bookings.serializers import BookingDetailSerializer
        if obj.booking:
            return {
                'id': obj.booking.id,
                'date': obj.booking.date,
                'start_time': obj.booking.start_time,
                'end_time': obj.booking.end_time,
                'status': obj.booking.status,
                'price': obj.booking.price,
            }
        return None


class PaymentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializers لإنشاء وتحديث المدفوعات"""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'amount', 'payment_type',
            'payment_method', 'reference_number', 'transaction_id',
            'description', 'receipt', 'payment_date', 'due_date',
            'status',
        ]
        read_only_fields = ['status']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('المبلغ يجب أن يكون أكبر من صفر')
        return value
    
    def validate(self, data):
        booking = data.get('booking')
        amount = data.get('amount')
        payment_type = data.get('payment_type')
        
        if not booking:
            raise serializers.ValidationError({
                'booking': 'يجب تحديد الحجز'
            })
        
        # ✅ التأكد من وجود سعر للحجز
        if not booking.price or booking.price <= 0:
            raise serializers.ValidationError({
                'booking': 'هذا الحجز ليس له سعر محدد'
            })
        
        # حساب المبلغ المتبقي
        total_paid = Payment.objects.filter(
            booking=booking,
            status=Payment.Status.PAID
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        remaining = booking.price - total_paid
        
        # ✅ لو المبلغ المتبقي صفر
        if remaining <= 0 and payment_type != Payment.PaymentTypes.EXTRA:
            raise serializers.ValidationError({
                'amount': 'هذا الحجز مدفوع بالكامل'
            })
        
        # التحقق من أن المبلغ لا يتجاوز المتبقي
        if amount > remaining and payment_type != Payment.PaymentTypes.EXTRA:
            raise serializers.ValidationError({
                'amount': f'المبلغ ({amount}) يتجاوز المتبقي من الحجز ({remaining})'
            })
        
        # إذا كان نوع الدفعة FULL، يجب أن يساوي المبلغ المتبقي
        if payment_type == Payment.PaymentTypes.FULL and amount != remaining:
            raise serializers.ValidationError({
                'amount': f'الدفعة الكاملة يجب أن تكون {remaining}'
            })
        
        return data
    
    def create(self, validated_data):
        validated_data['status'] = Payment.Status.PENDING
        
        # تعيين المستخدم المنشئ
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)


class PaymentConfirmSerializer(serializers.Serializer):
    """Serializers لتأكيد الدفع"""
    
    confirm = serializers.BooleanField(default=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        instance = self.context.get('instance')
        if instance and instance.is_paid:
            raise serializers.ValidationError('الدفعة مدفوعة بالفعل')
        if instance and instance.is_refunded:
            raise serializers.ValidationError('لا يمكن تأكيد دفعة مستردة')
        return data


class PaymentRefundSerializer(serializers.Serializer):
    """Serializers لاسترداد الدفع"""
    
    reason = serializers.CharField(required=True)
    
    def validate(self, data):
        instance = self.context.get('instance')
        if instance and not instance.is_paid:
            raise serializers.ValidationError('لا يمكن استرداد دفعة غير مدفوعة')
        if instance and instance.is_refunded:
            raise serializers.ValidationError('الدفعة مستردة بالفعل')
        return data


class PaymentReportSerializer(serializers.Serializer):
    """Serializers لتقارير المدفوعات"""
    
    total_payments = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_count = serializers.IntegerField()
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_count = serializers.IntegerField()
    pending_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    failed_count = serializers.IntegerField()
    failed_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    refunded_count = serializers.IntegerField()
    refunded_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    by_type = serializers.DictField()
    by_method = serializers.DictField()