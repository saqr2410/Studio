from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Booking
from .serializers import (
    BookingListSerializer,
    BookingDetailSerializer,
    BookingCreateUpdateSerializer,
    BookingCancelSerializer,
    BookingReportSerializer,
)
from users.permissions import IsAdmin, IsReceptionist, IsPhotographer, IsReceptionistOrAdmin


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة الحجوزات مع ميزات متقدمة
    
    Actions:
    - list: عرض جميع الحجوزات (مع فلترة)
    - create: إنشاء حجز جديد
    - retrieve: عرض تفاصيل حجز
    - update: تحديث حجز
    - partial_update: تحديث جزئي
    - destroy: حذف حجز (للإدمن فقط)
    - confirm: تأكيد حجز
    - cancel: إلغاء حجز
    - complete: إنهاء حجز
    - report: تقرير إحصائي
    - upcoming: الحجوزات القادمة
    - today: حجوزات اليوم
    """
    
    queryset = Booking.objects.select_related(
        'customer', 
        'photographer', 
        'package',
        'created_by'
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer__name', 'customer__phone', 'title', 'notes']
    ordering_fields = ['date', 'start_time', 'created_at', 'price']
    ordering = ['-date', '-start_time']
    
    def get_serializer_class(self):
        """اختيار الـ Serializer المناسب حسب الـ action"""
        if self.action == 'list':
            return BookingListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BookingCreateUpdateSerializer
        elif self.action == 'retrieve':
            return BookingDetailSerializer
        elif self.action == 'report':
            return BookingReportSerializer
        elif self.action == 'cancel':
            return BookingCancelSerializer
        return BookingDetailSerializer
    
    def get_permissions(self):
        """تحديد الصلاحيات حسب الـ action"""
        permissions_map = {
            'create': [IsReceptionistOrAdmin],
            'list': [IsReceptionistOrAdmin],
            'retrieve': [IsReceptionistOrAdmin],
            'update': [IsReceptionist],
            'partial_update': [IsReceptionist],
            'destroy': [IsAdmin],
            'confirm': [IsReceptionist],
            'cancel': [IsReceptionistOrAdmin],
            'complete': [IsPhotographer],
            'report': [IsAdmin],
            'upcoming': [IsReceptionistOrAdmin],
            'today': [IsReceptionistOrAdmin],
        }
        permission_classes = permissions_map.get(self.action, [IsAdmin])
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """تعيين من قام بالإنشاء عند الحفظ"""
        serializer.save(created_by=self.request.user)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Custom Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """تأكيد الحجز"""
        booking = self.get_object()
        
        if booking.is_cancelled:
            return Response(
                {'error': 'لا يمكن تأكيد حجز ملغي'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.confirm(request.user)
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """إلغاء الحجز"""
        booking = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'instance': booking})
        serializer.is_valid(raise_exception=True)
        
        booking.cancel(request.user)
        return Response({'message': 'تم إلغاء الحجز بنجاح'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """إنهاء الحجز"""
        booking = self.get_object()
        
        if booking.is_cancelled:
            return Response(
                {'error': 'لا يمكن إنهاء حجز ملغي'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.complete(request.user)
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """عرض الحجوزات القادمة"""
        bookings = self.get_queryset().filter(
            date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        )
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """عرض حجوزات اليوم"""
        today = timezone.now().date()
        bookings = self.get_queryset().filter(date=today)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """تقرير إحصائي للحجوزات"""
        # إحصائيات الحجوزات
        stats = Booking.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            confirmed=Count('id', filter=Q(status='confirmed')),
            done=Count('id', filter=Q(status='done')),
            cancelled=Count('id', filter=Q(status='cancelled')),
            total_revenue=Sum('price', filter=Q(status='done')),
        )
        
        # إحصائيات حسب الشهر
        monthly_stats = Booking.objects.filter(
            date__year=timezone.now().year
        ).values('date__month').annotate(
            count=Count('id'),
            revenue=Sum('price', filter=Q(status='done'))
        )
        
        return Response({
            **stats,
            'monthly_stats': monthly_stats
        })
    
    @action(detail=False, methods=['get'])
    def by_photographer(self, request):
        """حجوزات مصور معين"""
        photographer_id = request.query_params.get('photographer_id')
        if not photographer_id:
            return Response(
                {'error': 'يجب إرسال photographer_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bookings = self.get_queryset().filter(photographer_id=photographer_id)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """حجوزات عميل معين"""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'يجب إرسال customer_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bookings = self.get_queryset().filter(customer_id=customer_id)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def availability(self, request):
        """التحقق من توفر المصور في وقت معين"""
        photographer_id = request.query_params.get('photographer_id')
        date = request.query_params.get('date')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        
        if not all([photographer_id, date, start_time, end_time]):
            return Response(
                {'error': 'يجب إرسال جميع المعاملات'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conflicts = Booking.objects.filter(
            photographer_id=photographer_id,
            date=date,
            status__in=['pending', 'confirmed', 'in_progress']
        )
        
        for booking in conflicts:
            overlap = (
                start_time < booking.end_time and
                end_time > booking.start_time
            )
            if overlap:
                return Response({
                    'available': False,
                    'conflict_with': f"{booking.customer} ({booking.start_time} - {booking.end_time})"
                })
        
        return Response({'available': True})