from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Payment
from .serializers import (
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentCreateUpdateSerializer,
    PaymentConfirmSerializer,
    PaymentRefundSerializer,
    PaymentReportSerializer,
)
from users.permissions import IsAdmin, IsReceptionist, IsReceptionistOrAdmin


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة المدفوعات مع ميزات متقدمة
    """
    
    queryset = Payment.objects.select_related(
        'booking',
        'booking__customer',
        'booking__photographer',
        'created_by'
    ).order_by('-payment_date', '-created_at')
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'id', 'reference_number', 'transaction_id',
        'description', 'booking__customer__name',
        'booking__customer__phone'
    ]
    ordering_fields = ['amount', 'payment_date', 'created_at']
    ordering = ['-payment_date', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PaymentCreateUpdateSerializer
        elif self.action == 'retrieve':
            return PaymentDetailSerializer
        elif self.action == 'confirm':
            return PaymentConfirmSerializer
        elif self.action == 'refund':
            return PaymentRefundSerializer
        elif self.action == 'report':
            return PaymentReportSerializer
        return PaymentDetailSerializer
    
    def get_permissions(self):
        permissions_map = {
            'list': [IsReceptionistOrAdmin],
            'retrieve': [IsReceptionistOrAdmin],
            'create': [IsReceptionistOrAdmin],
            'update': [IsReceptionistOrAdmin],
            'partial_update': [IsReceptionistOrAdmin],
            'destroy': [IsAdmin],
            'confirm': [IsReceptionistOrAdmin],
            'fail': [IsReceptionistOrAdmin],
            'refund': [IsAdmin],
            'report': [IsAdmin],
            'by_booking': [IsReceptionistOrAdmin],
            'by_customer': [IsReceptionistOrAdmin],
            'monthly': [IsAdmin],
            'stats': [IsAdmin],
            'overdue': [IsReceptionistOrAdmin],
        }
        permission_classes = permissions_map.get(self.action, [IsAdmin])
        return [permission() for permission in permission_classes]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Custom Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """تأكيد الدفعة"""
        payment = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'instance': payment})
        serializer.is_valid(raise_exception=True)
        
        payment.confirm(request.user)
        
        # ✅ إنشاء إيراد من الدفعة
        from finance.models import Income
        Income.objects.get_or_create(
            booking=payment.booking,
            amount=payment.amount,
            source=Income.Source.BOOKING,
            defaults={
                'title': f'دفعة من حجز #{payment.booking.id}',
                'payment_method': payment.payment_method,
                'customer': payment.booking.customer,
                'income_date': payment.payment_date,
                'description': f'دفعة #{payment.id}',
            }
        )
        
        # تحديث حالة الحجز إذا كانت الدفعة كاملة
        if payment.is_full or payment.amount == payment.remaining_balance:
            if payment.booking and payment.booking.status != 'confirmed':
                payment.booking.confirm(request.user)
        
        return Response({
            'message': 'تم تأكيد الدفعة بنجاح',
            'payment': PaymentDetailSerializer(payment).data
        })
    
    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        """تسجيل فشل الدفعة"""
        payment = self.get_object()
        if payment.is_paid:
            return Response(
                {'error': 'لا يمكن تغيير حالة دفعة مدفوعة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        payment.fail(request.user)
        return Response({
            'message': 'تم تسجيل فشل الدفعة',
            'payment': PaymentDetailSerializer(payment).data
        })
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """استرداد الدفعة"""
        payment = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'instance': payment})
        serializer.is_valid(raise_exception=True)
        
        payment.refund(request.user)
        return Response({
            'message': 'تم استرداد الدفعة بنجاح',
            'payment': PaymentDetailSerializer(payment).data
        })
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """تقرير المدفوعات"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        
        total_count = queryset.count()
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        paid_queryset = queryset.filter(status=Payment.Status.PAID)
        pending_queryset = queryset.filter(status=Payment.Status.PENDING)
        failed_queryset = queryset.filter(status=Payment.Status.FAILED)
        refunded_queryset = queryset.filter(status=Payment.Status.REFUNDED)
        
        by_type = dict(
            queryset.values('payment_type').annotate(
                total=Sum('amount')
            ).values_list('payment_type', 'total')
        )
        
        by_method = dict(
            queryset.values('payment_method').annotate(
                total=Sum('amount')
            ).values_list('payment_method', 'total')
        )
        
        data = {
            'total_payments': total_count,
            'total_amount': total_amount,
            'paid_count': paid_queryset.count(),
            'paid_amount': paid_queryset.aggregate(total=Sum('amount'))['total'] or 0,
            'pending_count': pending_queryset.count(),
            'pending_amount': pending_queryset.aggregate(total=Sum('amount'))['total'] or 0,
            'failed_count': failed_queryset.count(),
            'failed_amount': failed_queryset.aggregate(total=Sum('amount'))['total'] or 0,
            'refunded_count': refunded_queryset.count(),
            'refunded_amount': refunded_queryset.aggregate(total=Sum('amount'))['total'] or 0,
            'by_type': by_type,
            'by_method': by_method,
        }
        
        serializer = self.get_serializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_booking(self, request):
        """المدفوعات حسب الحجز"""
        booking_id = request.query_params.get('booking_id')
        if not booking_id:
            return Response(
                {'error': 'يجب إرسال booking_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payments = self.get_queryset().filter(booking_id=booking_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """المدفوعات حسب العميل"""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'يجب إرسال customer_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payments = self.get_queryset().filter(booking__customer_id=customer_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def monthly(self, request):
        """إجمالي المدفوعات الشهرية"""
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response(
                {'error': 'يجب إدخال سنة وشهر صحيحين'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        total = Payment.get_monthly_totals(year, month)
        
        return Response({
            'year': year,
            'month': month,
            'total': total
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """إحصائيات سريعة للمدفوعات"""
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        today_total = Payment.objects.filter(
            payment_date__date=today,
            status=Payment.Status.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_total = Payment.objects.filter(
            payment_date__date__gte=start_of_month,
            payment_date__date__lte=today,
            status=Payment.Status.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        today_count = Payment.objects.filter(
            payment_date__date=today,
            status=Payment.Status.PAID
        ).count()
        
        return Response({
            'today': {
                'count': today_count,
                'total': today_total,
            },
            'month': {
                'total': month_total,
            },
            'pending_count': Payment.objects.filter(status=Payment.Status.PENDING).count(),
            'pending_amount': Payment.objects.filter(
                status=Payment.Status.PENDING
            ).aggregate(total=Sum('amount'))['total'] or 0,
        })
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """المدفوعات المتأخرة"""
        now = timezone.now()
        payments = self.get_queryset().filter(
            due_date__lt=now,
            status__in=[Payment.Status.PENDING, Payment.Status.PARTIAL]
        )
        
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)