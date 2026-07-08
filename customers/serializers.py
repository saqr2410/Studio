from rest_framework import serializers
from django.core.validators import validate_email
from .models import Customer


class CustomerListSerializer(serializers.ModelSerializer):
    """Serializers لعرض العملاء (خفيف)"""
    
    status_badge = serializers.ReadOnlyField()
    display_phone = serializers.ReadOnlyField()
    contact_info = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'display_phone', 'email',
            'customer_type', 'is_active', 'is_blacklisted',
            'status_badge', 'contact_info',
            'total_bookings', 'total_spent',
            'created_at'
        ]


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Serializers لعرض تفاصيل العميل (كامل)"""
    
    # Fields من العلاقات
    preferred_photographer_name = serializers.CharField(
        source='preferred_photographer.get_full_name',
        read_only=True
    )
    preferred_package_name = serializers.CharField(
        source='preferred_package.name',
        read_only=True
    )
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    
    # Properties
    age = serializers.ReadOnlyField()
    is_vip = serializers.ReadOnlyField()
    status_badge = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'phone', 'email',
            'gender', 'customer_type', 'date_of_birth', 'age',
            'address', 'city', 'country',
            'instagram', 'facebook', 'twitter', 'website',
            'preferred_photographer', 'preferred_photographer_name',
            'preferred_package', 'preferred_package_name',
            'preferred_contact_method',
            'notes', 'is_active', 'is_blacklisted', 'blacklist_reason',
            'total_bookings', 'total_spent', 'last_booking_date',
            'created_at', 'updated_at',
            'created_by', 'created_by_name',
            'is_vip', 'status_badge'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'total_bookings',
            'total_spent', 'last_booking_date'
        ]


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializers لإنشاء وتحديث العملاء"""
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'phone', 'email',
            'gender', 'customer_type', 'date_of_birth',
            'address', 'city', 'country',
            'instagram', 'facebook', 'twitter', 'website',
            'preferred_photographer', 'preferred_package',
            'preferred_contact_method',
            'notes', 'is_active', 'is_blacklisted', 'blacklist_reason',
        ]
    
    def validate_phone(self, value):
        """التحقق من رقم الهاتف"""
        # إزالة المسافات الزائدة
        value = value.strip()
        
        # التحقق من الطول
        if len(value) < 10:
            raise serializers.ValidationError('رقم الهاتف قصير جداً')
        
        # التحقق من عدم التكرار
        if Customer.objects.filter(phone=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError('رقم الهاتف موجود بالفعل')
        
        return value
    
    def validate_email(self, value):
        """التحقق من البريد الإلكتروني"""
        # ✅ التحقق فقط لو مش فاضي
        if value and value.strip():
            value = value.strip().lower()
            try:
                validate_email(value)
            except:
                raise serializers.ValidationError('بريد إلكتروني غير صحيح')
            
            # التحقق من عدم التكرار
            if Customer.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
                raise serializers.ValidationError('البريد الإلكتروني موجود بالفعل')
        
        return value
    
    def validate(self, data):
        """التحقق المتقدم"""
        # التحقق من أن العميل المحظور لديه سبب
        if data.get('is_blacklisted') and not data.get('blacklist_reason'):
            raise serializers.ValidationError({
                'blacklist_reason': 'يجب إدخال سبب الحظر'
            })
        
        # التحقق من أن تاريخ الميلاد ليس في المستقبل
        if data.get('date_of_birth'):
            from django.utils import timezone
            if data['date_of_birth'] > timezone.now().date():
                raise serializers.ValidationError({
                    'date_of_birth': 'تاريخ الميلاد لا يمكن أن يكون في المستقبل'
                })
        
        return data


class CustomerBulkCreateSerializer(serializers.Serializer):
    """Serializers لإنشاء عملاء متعددين"""
    
    customers = CustomerCreateUpdateSerializer(many=True)
    
    def create(self, validated_data):
        created = []
        for customer_data in validated_data['customers']:
            customer = Customer.objects.create(**customer_data)
            created.append(customer)
        return created


class CustomerSearchSerializer(serializers.Serializer):
    """Serializers للبحث في العملاء"""
    
    query = serializers.CharField(required=True)
    limit = serializers.IntegerField(required=False, default=10)


class CustomerStatsSerializer(serializers.Serializer):
    """Serializers لإحصائيات العملاء"""
    
    total = serializers.IntegerField()
    active = serializers.IntegerField()
    vip = serializers.IntegerField()
    blacklisted = serializers.IntegerField()
    new_this_month = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_spent = serializers.DecimalField(max_digits=12, decimal_places=2)