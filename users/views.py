from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserChangePasswordSerializer,
    UserRoleChangeSerializer,
    UserProfileSerializer,
    UserStatsSerializer,
)
from .permissions import IsAdmin, IsReceptionist, IsReceptionistOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة المستخدمين مع ميزات متقدمة
    
    Actions:
    - list: عرض جميع المستخدمين
    - create: إنشاء مستخدم جديد
    - retrieve: عرض تفاصيل مستخدم
    - update: تحديث مستخدم
    - partial_update: تحديث جزئي
    - destroy: حذف مستخدم
    - me: الملف الشخصي للمستخدم الحالي
    - change_password: تغيير كلمة المرور
    - change_role: تغيير دور المستخدم
    - toggle_active: تفعيل/تعطيل المستخدم
    - stats: إحصائيات المستخدمين
    - photographers: قائمة المصورين
    - staff: قائمة الموظفين
    - search: بحث متقدم
    """
    
    queryset = User.objects.select_related('created_by').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'username', 'email', 'first_name', 'last_name',
        'phone', 'address', 'city'
    ]
    ordering_fields = ['username', 'email', 'created_at', 'last_active']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'me':
            return UserProfileSerializer
        elif self.action == 'change_password':
            return UserChangePasswordSerializer
        elif self.action == 'change_role':
            return UserRoleChangeSerializer
        elif self.action == 'stats':
            return UserStatsSerializer
        return UserDetailSerializer
    
    def get_permissions(self):
        permissions_map = {
            'list': [IsAuthenticated],
            'retrieve': [IsAuthenticated],
            'create': [IsAdmin],
            'update': [IsAdmin],
            'partial_update': [IsAdmin],
            'destroy': [IsAdmin],
            'me': [IsAuthenticated],
            'change_password': [IsAuthenticated],
            'change_role': [IsAdmin],
            'toggle_active': [IsAdmin],
            'stats': [IsAdmin],
            'photographers': [IsAuthenticated],
            'staff': [IsAdmin],
            'search': [IsReceptionistOrAdmin],
            'toggle_status': [IsAdmin],
        }
        permission_classes = permissions_map.get(self.action, [IsAdmin])
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # تعيين المستخدم المنشئ في حالة إنشاء مستخدم جديد
        serializer.save(created_by=self.request.user)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Custom Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """الملف الشخصي للمستخدم الحالي"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """تغيير كلمة المرور للمستخدم الحالي"""
        serializer = self.get_serializer(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        
        # تغيير كلمة المرور
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # إنشاء توكن جديد
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'تم تغيير كلمة المرور بنجاح',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def change_role(self, request, pk=None):
        """تغيير دور المستخدم"""
        user = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'instance': user}
        )
        serializer.is_valid(raise_exception=True)
        
        user.role = serializer.validated_data['role']
        user.save()
        
        return Response({
            'message': f'تم تغيير دور المستخدم إلى {user.get_role_display()}',
            'user': UserDetailSerializer(user).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def toggle_active(self, request, pk=None):
        """تفعيل/تعطيل المستخدم"""
        user = self.get_object()
        
        # منع تعطيل آخر مدير
        if user.is_admin and User.objects.filter(role=User.Roles.ADMIN).count() <= 1:
            return Response(
                {'error': 'لا يمكن تعطيل آخر مدير في النظام'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'message': f'تم {"تفعيل" if user.is_active else "تعطيل"} المستخدم',
            'user': UserDetailSerializer(user).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def toggle_status(self, request, pk=None):
        """تغيير حالة المستخدم"""
        user = self.get_object()
        status_value = request.data.get('status')
        
        if status_value not in [choice[0] for choice in User.Status.choices]:
            return Response(
                {'error': 'حالة غير صالحة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # منع تغيير حالة آخر مدير
        if user.is_admin and User.objects.filter(role=User.Roles.ADMIN).count() <= 1:
            return Response(
                {'error': 'لا يمكن تغيير حالة آخر مدير في النظام'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.status = status_value
        user.save()
        
        return Response({
            'message': f'تم تغيير حالة المستخدم إلى {user.get_status_display()}',
            'user': UserDetailSerializer(user).data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    def stats(self, request):
        """إحصائيات المستخدمين"""
        now = timezone.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True, status=User.Status.ACTIVE).count(),
            'by_role': dict(
                User.objects.values('role').annotate(count=Count('id'))
                .values_list('role', 'count')
            ),
            'by_status': dict(
                User.objects.values('status').annotate(count=Count('id'))
                .values_list('status', 'count')
            ),
            'new_users_this_month': User.objects.filter(created_at__gte=first_day_of_month).count(),
            'photographers_count': User.objects.filter(role=User.Roles.PHOTOGRAPHER, is_active=True).count(),
            'online_now': User.objects.filter(last_active__gte=timezone.now() - timezone.timedelta(minutes=5)).count(),
        }
        
        serializer = self.get_serializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def photographers(self, request):
        """قائمة المصورين النشطين"""
        photographers = User.get_photographers()
        serializer = self.get_serializer(photographers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    def staff(self, request):
        """قائمة الموظفين (جميع الأدوار ما عدا Admin)"""
        staff = User.objects.filter(is_active=True).exclude(role=User.Roles.ADMIN)
        serializer = self.get_serializer(staff, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """بحث متقدم في المستخدمين"""
        query = request.query_params.get('q', '')
        role = request.query_params.get('role', '')
        status_param = request.query_params.get('status', '')
        
        if not query:
            return Response(
                {'error': 'يجب إدخال نص للبحث'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query)
        )
        
        if role:
            queryset = queryset.filter(role=role)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """المستخدمين حسب الدور"""
        role = request.query_params.get('role')
        if not role:
            return Response(
                {'error': 'يجب إرسال role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if role not in [choice[0] for choice in User.Roles.choices]:
            return Response(
                {'error': 'دور غير صحيح'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(role=role, is_active=True)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)