from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Customer
from .serializers import (
    CustomerListSerializer,
    CustomerDetailSerializer,
    CustomerCreateUpdateSerializer,
    CustomerBulkCreateSerializer,
    CustomerSearchSerializer,
    CustomerStatsSerializer,
)
from users.permissions import IsAdmin, IsReceptionist, IsReceptionistOrAdmin


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة العملاء مع ميزات متقدمة
    
    Actions:
    - list: عرض جميع العملاء (مع فلترة)
    - create: إنشاء عميل جديد
    - retrieve: عرض تفاصيل عميل
    - update: تحديث عميل
    - partial_update: تحديث جزئي
    - destroy: حذف عميل (للإدمن فقط)
    - stats: إحصائيات العملاء
    - search: بحث متقدم
    - vip: قائمة عملاء VIP
    - active: قائمة العملاء النشطين
    - blacklist: حظر عميل
    - unblacklist: إلغاء حظر عميل
    - bookings: حجوزات العميل
    """
    
    queryset = Customer.objects.select_related(
        'preferred_photographer',
        'preferred_package',
        'created_by'
    ).prefetch_related('bookings')
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone', 'email', 'address', 'notes']
    ordering_fields = ['name', 'created_at', 'total_bookings', 'total_spent']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """اختيار الـ Serializer المناسب حسب الـ action"""
        if self.action == 'list':
            return CustomerListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CustomerCreateUpdateSerializer
        elif self.action == 'retrieve':
            return CustomerDetailSerializer
        elif self.action == 'stats':
            return CustomerStatsSerializer
        elif self.action == 'search':
            return CustomerSearchSerializer
        return CustomerDetailSerializer
    
    def get_permissions(self):
        """تحديد الصلاحيات حسب الـ action"""
        permissions_map = {
            'list': [IsReceptionistOrAdmin],
            'retrieve': [IsReceptionistOrAdmin],
            'create': [IsReceptionistOrAdmin],  # ✅ تم التعديل
            'update': [IsReceptionistOrAdmin],   # ✅ تم التعديل
            'partial_update': [IsReceptionistOrAdmin],  # ✅ تم التعديل
            'destroy': [IsAdmin],
            'stats': [IsAdmin],
            'search': [IsReceptionistOrAdmin],
            'vip': [IsReceptionistOrAdmin],
            'active': [IsReceptionistOrAdmin],
            'blacklist': [IsReceptionistOrAdmin],  # ✅ تم التعديل
            'unblacklist': [IsReceptionistOrAdmin],  # ✅ تم التعديل
            'bookings': [IsReceptionistOrAdmin],
        }
        permission_classes = permissions_map.get(self.action, [IsAdmin])
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """تعيين من قام بالإنشاء عند الحفظ"""
        serializer.save(created_by=self.request.user)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Custom Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """إحصائيات العملاء"""
        from django.db.models import Sum, Q
        
        now = timezone.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        stats = {
            'total': Customer.objects.count(),
            'active': Customer.objects.filter(is_active=True, is_blacklisted=False).count(),
            'vip': Customer.objects.filter(customer_type=Customer.TYPE_VIP, is_active=True).count(),
            'blacklisted': Customer.objects.filter(is_blacklisted=True).count(),
            'new_this_month': Customer.objects.filter(created_at__gte=first_day_of_month).count(),
        }
        
        # إجمالي الإيرادات من العملاء
        total_spent = Customer.objects.aggregate(total=Sum('total_spent'))['total'] or 0
        stats['total_revenue'] = total_spent
        
        # متوسط الإنفاق
        total_customers = Customer.objects.filter(total_spent__gt=0).count()
        if total_customers > 0:
            stats['average_spent'] = total_spent / total_customers
        else:
            stats['average_spent'] = 0
        
        serializer = self.get_serializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """بحث متقدم في العملاء"""
        query = request.query_params.get('q', '')
        customer_type = request.query_params.get('type', '')
        is_vip = request.query_params.get('vip', '')
        
        if not query:
            return Response(
                {'error': 'يجب إدخال نص للبحث'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(address__icontains=query)
        )
        
        if customer_type:
            queryset = queryset.filter(customer_type=customer_type)
        
        if is_vip and is_vip.lower() == 'true':
            queryset = queryset.filter(customer_type=Customer.TYPE_VIP)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vip(self, request):
        """قائمة عملاء VIP"""
        customers = Customer.objects.filter(
            customer_type=Customer.TYPE_VIP,
            is_active=True,
            is_blacklisted=False
        )
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """قائمة العملاء النشطين"""
        customers = Customer.get_active_customers()
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def blacklisted(self, request):
        """قائمة العملاء المحظورين"""
        customers = Customer.objects.filter(is_blacklisted=True)
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def blacklist(self, request, pk=None):
        """حظر عميل"""
        customer = self.get_object()
        reason = request.data.get('reason', '')
        
        if not reason:
            return Response(
                {'error': 'يجب إدخال سبب الحظر'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer.is_blacklisted = True
        customer.blacklist_reason = reason
        customer.save()
        
        serializer = self.get_serializer(customer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unblacklist(self, request, pk=None):
        """إلغاء حظر عميل"""
        customer = self.get_object()
        customer.is_blacklisted = False
        customer.blacklist_reason = ''
        customer.save()
        
        serializer = self.get_serializer(customer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """عرض حجوزات العميل"""
        customer = self.get_object()
        from bookings.serializers import BookingListSerializer
        
        bookings = customer.bookings.select_related('photographer').order_by('-date', '-start_time')
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_stats(self, request, pk=None):
        """تحديث إحصائيات العميل"""
        customer = self.get_object()
        customer.update_stats()
        
        serializer = self.get_serializer(customer)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """إنشاء عملاء متعددين دفعة واحدة"""
        serializer = CustomerBulkCreateSerializer(data=request.data)
        if serializer.is_valid():
            customers = serializer.create(serializer.validated_data)
            return Response(
                CustomerListSerializer(customers, many=True).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def top_customers(self, request):
        """أفضل العملاء من حيث الإنفاق"""
        limit = int(request.query_params.get('limit', 10))
        customers = Customer.objects.filter(
            is_active=True,
            is_blacklisted=False
        ).order_by('-total_spent')[:limit]
        
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)