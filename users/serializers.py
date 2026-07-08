from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from .models import User


class UserListSerializer(serializers.ModelSerializer):
    """Serializers لعرض المستخدمين (خفيف)"""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'email', 'phone',
            'role', 'role_display', 'status', 'status_display',
            'is_active', 'is_verified', 'last_active',
            'created_at'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializers لعرض تفاصيل المستخدم (كامل)"""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    is_admin = serializers.ReadOnlyField()
    is_photographer = serializers.ReadOnlyField()
    is_active_user = serializers.ReadOnlyField()
    
    dashboard_redirect = serializers.ReadOnlyField()
    permissions_list = serializers.ReadOnlyField()
    
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    # إحصائيات إضافية
    bookings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'gender', 'gender_display',
            'date_of_birth', 'age',
            'profile_picture', 'bio',
            'address', 'city', 'country',
            'role', 'role_display', 'status', 'status_display',
            'is_active', 'is_verified', 'is_active_user',
            'is_admin', 'is_photographer',
            'skills', 'specialties',
            'notification_preferences',
            'theme_preference', 'language', 'timezone',
            'hire_date', 'last_active',
            'created_at', 'updated_at',
            'created_by', 'created_by_name',
            'dashboard_redirect', 'permissions_list',
            'bookings_count',
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_active']
    
    def get_bookings_count(self, obj):
        """عدد الحجوزات للمستخدم"""
        if hasattr(obj, 'bookings'):
            return obj.bookings.count()
        return 0


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializers لإنشاء مستخدم جديد"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'phone', 'password', 'confirm_password',
            'role', 'gender', 'date_of_birth',
            'address', 'city', 'country',
            'profile_picture', 'bio',
            'status', 'is_active', 'is_verified',
            'hire_date',
            'skills', 'specialties',
            'theme_preference', 'language', 'timezone',
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }
    
    def validate_username(self, value):
        """التحقق من اسم المستخدم"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('اسم المستخدم موجود بالفعل')
        return value
    
    def validate_email(self, value):
        """التحقق من البريد الإلكتروني"""
        if value:
            try:
                validate_email(value)
            except:
                raise serializers.ValidationError('بريد إلكتروني غير صحيح')
            
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError('البريد الإلكتروني موجود بالفعل')
        return value
    
    def validate(self, data):
        """التحقق من تطابق كلمة المرور"""
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'كلمة المرور غير متطابقة'
            })
        
        # التحقق من أن تاريخ الميلاد ليس في المستقبل
        if data.get('date_of_birth'):
            from django.utils import timezone
            if data['date_of_birth'] > timezone.now().date():
                raise serializers.ValidationError({
                    'date_of_birth': 'تاريخ الميلاد لا يمكن أن يكون في المستقبل'
                })
        
        return data
    
    def create(self, validated_data):
        # إزالة confirm_password
        validated_data.pop('confirm_password')
        
        # استخراج كلمة المرور
        password = validated_data.pop('password')
        
        # إنشاء المستخدم
        user = User(**validated_data)
        user.set_password(password)
        
        # تعيين المستخدم المنشئ
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user.created_by = request.user
        
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializers لتحديث المستخدم"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'phone', 'gender', 'date_of_birth',
            'address', 'city', 'country',
            'profile_picture', 'bio',
            'role', 'status', 'is_active', 'is_verified',
            'skills', 'specialties',
            'notification_preferences',
            'theme_preference', 'language', 'timezone',
        ]
        read_only_fields = ['id']
    
    def validate_email(self, value):
        """التحقق من البريد الإلكتروني"""
        if value:
            try:
                validate_email(value)
            except:
                raise serializers.ValidationError('بريد إلكتروني غير صحيح')
            
            if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('البريد الإلكتروني موجود بالفعل')
        return value
    
    def validate(self, data):
        """التحقق من تاريخ الميلاد"""
        if data.get('date_of_birth'):
            from django.utils import timezone
            if data['date_of_birth'] > timezone.now().date():
                raise serializers.ValidationError({
                    'date_of_birth': 'تاريخ الميلاد لا يمكن أن يكون في المستقبل'
                })
        return data


class UserChangePasswordSerializer(serializers.Serializer):
    """Serializers لتغيير كلمة المرور"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    confirm_new_password = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        """التحقق من كلمة المرور القديمة"""
        user = self.context.get('user')
        if not user.check_password(value):
            raise serializers.ValidationError('كلمة المرور القديمة غير صحيحة')
        return value
    
    def validate(self, data):
        """التحقق من تطابق كلمة المرور الجديدة"""
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({
                'confirm_new_password': 'كلمة المرور الجديدة غير متطابقة'
            })
        return data


class UserRoleChangeSerializer(serializers.Serializer):
    """Serializers لتغيير دور المستخدم"""
    
    role = serializers.ChoiceField(choices=User.Roles.choices)
    
    def validate(self, data):
        """التحقق من أن المستخدم ليس آخر مدير"""
        if self.context.get('instance') and self.context['instance'].is_admin:
            admin_count = User.objects.filter(role=User.Roles.ADMIN).count()
            if admin_count <= 1 and data['role'] != User.Roles.ADMIN:
                raise serializers.ValidationError(
                    'لا يمكن تغيير دور آخر مدير في النظام'
                )
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializers للملف الشخصي للمستخدم الحالي"""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.ReadOnlyField()
    dashboard_redirect = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'gender', 'date_of_birth',
            'profile_picture', 'bio',
            'address', 'city', 'country',
            'role', 'role_display',
            'theme_preference', 'language', 'timezone',
            'dashboard_redirect',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'role', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        # منع تغيير بعض الحقول
        validated_data.pop('role', None)
        validated_data.pop('username', None)
        return super().update(instance, validated_data)


class UserStatsSerializer(serializers.Serializer):
    """Serializers لإحصائيات المستخدمين"""
    
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    by_role = serializers.DictField()
    by_status = serializers.DictField()
    new_users_this_month = serializers.IntegerField()
    photographers_count = serializers.IntegerField()
    online_now = serializers.IntegerField()