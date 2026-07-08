from rest_framework import serializers
from django.utils import timezone
from django.db.models import Q
from .models import Booking


class BookingListSerializer(serializers.ModelSerializer):
    """Serializers لعرض الحجوزات (خفيف)"""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    photographer_name = serializers.CharField(source='photographer.get_full_name', read_only=True)
    status_display = serializers.CharField(read_only=True)  # ✅ من غير source
    
    class Meta:
        model = Booking
        fields = [
            'id', 'title', 'date', 'start_time', 'end_time',
            'customer_name', 'photographer_name',
            'status', 'status_display', 'price',
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    """Serializers لعرض تفاصيل الحجز (كامل)"""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    
    photographer_name = serializers.CharField(source='photographer.get_full_name', read_only=True)
    photographer_phone = serializers.CharField(source='photographer.phone', read_only=True)
    
    status_display = serializers.CharField(read_only=True)  # ✅ من غير source
    duration = serializers.ReadOnlyField(source='duration_in_hours')
    remaining = serializers.ReadOnlyField(source='remaining_payment')
    total_with_tax = serializers.ReadOnlyField(source='total_price')
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'title', 'date', 'start_time', 'end_time', 'duration',
            'customer', 'customer_name', 'customer_phone', 'customer_email',
            'photographer', 'photographer_name', 'photographer_phone',
            'package', 'price', 'deposit', 'remaining', 'total_with_tax',
            'status', 'status_display', 'location', 'is_onsite',
            'notes', 'rating', 'feedback',
            'created_at', 'updated_at', 'confirmed_at', 'cancelled_at', 'completed_at',
            'created_by', 'created_by_name',
            'is_confirmed', 'is_cancelled', 'is_done', 'is_pending',
            'is_upcoming', 'is_ongoing',
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'confirmed_at', 
            'cancelled_at', 'completed_at'
        ]


class BookingCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializers لإنشاء وتحديث الحجوزات"""
    
    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'photographer', 'title', 'date',
            'start_time', 'end_time', 'package', 'price', 'deposit',
            'location', 'is_onsite', 'notes', 'status'
        ]
    
    def validate(self, data):
        """التحقق من صحة البيانات"""
        
        # 1. التأكد من أن وقت النهاية بعد البداية
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        if end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'وقت النهاية يجب أن يكون بعد وقت البداية'
            })
        
        # 2. التأكد من أن التاريخ ليس في الماضي
        date = data.get('date')
        if date < timezone.now().date():
            raise serializers.ValidationError({
                'date': 'لا يمكن الحجز في تاريخ سابق'
            })
        
        # 3. التحقق من عدم وجود تعارض مع حجوزات أخرى
        photographer = data.get('photographer')
        booking_id = self.instance.id if self.instance else None
        
        conflicts = Booking.objects.filter(
            photographer=photographer,
            date=date,
            status__in=['pending', 'confirmed', 'in_progress']
        ).exclude(id=booking_id)
        
        for booking in conflicts:
            overlap = (
                start_time < booking.end_time and
                end_time > booking.start_time
            )
            if overlap:
                raise serializers.ValidationError({
                    'start_time': f'المصور محجوز في هذا الوقت ({booking.start_time} - {booking.end_time})'
                })
        
        return data
    
    def validate_price(self, value):
        """التحقق من السعر"""
        if value and value < 0:
            raise serializers.ValidationError('السعر لا يمكن أن يكون سالباً')
        return value
    
    def validate_deposit(self, value):
        """التحقق من الدفعة المقدمة"""
        price = self.initial_data.get('price', 0)
        if value and value > float(price):
            raise serializers.ValidationError(
                'الدفعة المقدمة لا يمكن أن تتجاوز السعر الإجمالي'
            )
        return value


class BookingCancelSerializer(serializers.Serializer):
    """Serializers لإلغاء الحجز مع سبب"""
    
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        instance = self.context.get('instance')
        if instance and instance.is_done:
            raise serializers.ValidationError(
                'لا يمكن إلغاء حجز منتهي'
            )
        if instance and instance.is_cancelled:
            raise serializers.ValidationError(
                'الحجز ملغي بالفعل'
            )
        return data


class BookingReportSerializer(serializers.Serializer):
    """Serializers لتقارير الحجوزات"""
    
    total_bookings = serializers.IntegerField()
    pending = serializers.IntegerField()
    confirmed = serializers.IntegerField()
    done = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)