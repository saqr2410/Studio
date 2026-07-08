from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.utils.dateformat import DateFormat
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Expense, Income
from .serializers import (
    ExpenseListSerializer,
    ExpenseDetailSerializer,
    ExpenseCreateUpdateSerializer,
    ExpenseBulkCreateSerializer,
    IncomeListSerializer,
    IncomeDetailSerializer,
    IncomeCreateUpdateSerializer,
    FinanceSummarySerializer,
    FinanceMonthlySerializer,
    FinanceYearlySerializer,
)
from users.permissions import IsAdmin, IsReceptionist, IsReceptionistOrAdmin
from payments.models import Payment  # ✅ استورد Payment


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 EXPENSE VIEWSET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة المصروفات
    """
    
    queryset = Expense.objects.select_related(
        'project', 'booking', 'created_by'
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'vendor', 'receipt_number']
    ordering_fields = ['amount', 'expense_date', 'created_at']
    ordering = ['-expense_date', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExpenseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ExpenseCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ExpenseDetailSerializer
        return ExpenseDetailSerializer
    
    def get_permissions(self):
        permissions_map = {
            'list': [IsReceptionistOrAdmin],
            'retrieve': [IsReceptionistOrAdmin],
            'create': [IsReceptionist],
            'update': [IsReceptionist],
            'partial_update': [IsReceptionist],
            'destroy': [IsAdmin],
            'mark_paid': [IsReceptionist],
            'cancel': [IsReceptionist],
            'stats_by_category': [IsAdmin],
            'monthly_totals': [IsAdmin],
        }
        permission_classes = permissions_map.get(self.action, [IsAdmin])
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Custom Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """تحديث المصروف كمدفوع"""
        expense = self.get_object()
        if expense.is_paid:
            return Response(
                {'message': 'المصروف مدفوع بالفعل'},
                status=status.HTTP_400_BAD_REQUEST
            )
        expense.mark_paid()
        serializer = self.get_serializer(expense)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """إلغاء المصروف"""
        expense = self.get_object()
        if expense.is_paid:
            return Response(
                {'message': 'لا يمكن إلغاء مصروف مدفوع'},
                status=status.HTTP_400_BAD_REQUEST
            )
        expense.cancel()
        serializer = self.get_serializer(expense)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats_by_category(self, request):
        """إحصائيات المصروفات حسب التصنيف"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        stats = Expense.get_total_by_category(start_date, end_date)
        
        # إضافة أسماء التصنيفات
        result = []
        for item in stats:
            result.append({
                'category': item['category'],
                'category_display': dict(Expense.Category.choices).get(item['category'], item['category']),
                'total': item['total']
            })
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def monthly_totals(self, request):
        """إجمالي المصروفات الشهرية"""
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
        
        total = Expense.get_monthly_totals(year, month)
        
        return Response({
            'year': year,
            'month': month,
            'total': total
        })
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """المصروفات حسب المشروع"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {'error': 'يجب إرسال project_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expenses = self.get_queryset().filter(project_id=project_id)
        serializer = self.get_serializer(expenses, many=True)
        return Response(serializer.data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 INCOME VIEWSET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class IncomeViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة الإيرادات
    """
    
    queryset = Income.objects.select_related(
        'booking', 'customer', 'project', 'created_by'
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'notes', 'invoice_number']
    ordering_fields = ['amount', 'income_date', 'created_at']
    ordering = ['-income_date', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return IncomeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return IncomeCreateUpdateSerializer
        elif self.action == 'retrieve':
            return IncomeDetailSerializer
        return IncomeDetailSerializer
    
    def get_permissions(self):
        permissions_map = {
            'list': [IsReceptionistOrAdmin],
            'retrieve': [IsReceptionistOrAdmin],
            'create': [IsReceptionist],
            'update': [IsReceptionist],
            'partial_update': [IsReceptionist],
            'destroy': [IsAdmin],
            'stats_by_source': [IsAdmin],
            'monthly_totals': [IsAdmin],
            'by_booking': [IsReceptionistOrAdmin],
            'by_customer': [IsReceptionistOrAdmin],
        }
        permission_classes = permissions_map.get(self.action, [IsAdmin])
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Custom Actions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=False, methods=['get'])
    def stats_by_source(self, request):
        """إحصائيات الإيرادات حسب المصدر"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        stats = Income.get_total_by_source(start_date, end_date)
        
        result = []
        for item in stats:
            result.append({
                'source': item['source'],
                'source_display': dict(Income.Source.choices).get(item['source'], item['source']),
                'total': item['total']
            })
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def monthly_totals(self, request):
        """إجمالي الإيرادات الشهرية"""
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
        
        total = Income.get_monthly_totals(year, month)
        
        return Response({
            'year': year,
            'month': month,
            'total': total
        })
    
    @action(detail=False, methods=['get'])
    def by_booking(self, request):
        """الإيرادات حسب الحجز"""
        booking_id = request.query_params.get('booking_id')
        if not booking_id:
            return Response(
                {'error': 'يجب إرسال booking_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        incomes = self.get_queryset().filter(booking_id=booking_id)
        serializer = self.get_serializer(incomes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """الإيرادات حسب العميل"""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'يجب إرسال customer_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        incomes = self.get_queryset().filter(customer_id=customer_id)
        serializer = self.get_serializer(incomes, many=True)
        return Response(serializer.data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 FINANCE VIEWSET (التقارير المالية)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class FinanceViewSet(viewsets.ViewSet):
    """
    ViewSet للتقارير المالية المتقدمة
    """
    
    permission_classes = [IsAuthenticated]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Summary
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def list(self, request):
        """الملخص المالي العام"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # ✅ الإيرادات من المدفوعات المؤكدة
        payments_queryset = Payment.objects.filter(status=Payment.Status.PAID)
        if start_date:
            payments_queryset = payments_queryset.filter(payment_date__gte=start_date)
        if end_date:
            payments_queryset = payments_queryset.filter(payment_date__lte=end_date)
        
        total_income = payments_queryset.aggregate(total=Sum('amount'))['total'] or 0
        income_count = payments_queryset.count()
        
        # المصروفات
        expense_qs = Expense.objects.all()
        if start_date:
            expense_qs = expense_qs.filter(expense_date__gte=start_date)
        if end_date:
            expense_qs = expense_qs.filter(expense_date__lte=end_date)
        
        total_expenses = expense_qs.aggregate(total=Sum('amount'))['total'] or 0
        expense_count = expense_qs.count()
        
        # الأرباح
        profit = total_income - total_expenses
        
        # التوزيع حسب التصنيف للمصروفات
        expenses_by_category = dict(
            expense_qs.values('category').annotate(
                total=Sum('amount')
            ).values_list('category', 'total')
        )
        
        # هامش الربح
        profit_margin = 0
        if total_income > 0:
            profit_margin = (profit / total_income) * 100
        
        data = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'profit': profit,
            'profit_margin': round(profit_margin, 2),
            'income_count': income_count,
            'expense_count': expense_count,
            'income_by_source': {'payments': total_income},
            'expenses_by_category': expenses_by_category,
        }
        
        return Response(data)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Monthly Report
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=False, methods=['get'])
    def monthly(self, request):
        """تقرير شهري"""
        year = request.query_params.get('year', timezone.now().year)
        try:
            year = int(year)
        except ValueError:
            return Response(
                {'error': 'يجب إدخال سنة صحيحة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = []
        for month in range(1, 13):
            # ✅ الإيرادات من المدفوعات
            monthly_income = Payment.objects.filter(
                payment_date__year=year,
                payment_date__month=month,
                status=Payment.Status.PAID
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # المصروفات
            monthly_expenses = Expense.objects.filter(
                expense_date__year=year,
                expense_date__month=month
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            profit = monthly_income - monthly_expenses
            
            data.append({
                'month': f'{month:02d}',
                'year': year,
                'income': monthly_income,
                'expenses': monthly_expenses,
                'profit': profit,
            })
        
        return Response(data)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Yearly Report
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=False, methods=['get'])
    def yearly(self, request):
        """تقرير سنوي"""
        start_year = request.query_params.get('start_year', timezone.now().year - 5)
        end_year = request.query_params.get('end_year', timezone.now().year)
        
        try:
            start_year = int(start_year)
            end_year = int(end_year)
        except ValueError:
            return Response(
                {'error': 'يجب إدخال سنوات صحيحة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = []
        for year in range(start_year, end_year + 1):
            # ✅ الإيرادات من المدفوعات
            total_income = Payment.objects.filter(
                payment_date__year=year,
                status=Payment.Status.PAID
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            total_expenses = Expense.objects.filter(
                expense_date__year=year,
                status=Expense.Status.PAID
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            profit = total_income - total_expenses
            
            # البيانات الشهرية لهذه السنة
            monthly_data = []
            for month in range(1, 13):
                monthly_income = Payment.objects.filter(
                    payment_date__year=year,
                    payment_date__month=month,
                    status=Payment.Status.PAID
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                monthly_expenses = Expense.objects.filter(
                    expense_date__year=year,
                    expense_date__month=month
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                monthly_data.append({
                    'month': f'{month:02d}',
                    'year': year,
                    'income': monthly_income,
                    'expenses': monthly_expenses,
                    'profit': monthly_income - monthly_expenses,
                })
            
            data.append({
                'year': year,
                'total_income': total_income,
                'total_expenses': total_expenses,
                'profit': profit,
                'monthly_data': monthly_data,
            })
        
        return Response(data)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Cash Flow
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=False, methods=['get'])
    def cash_flow(self, request):
        """التدفق النقدي"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # استخدام الفترة الحالية إن لم تُحدد
        if not start_date or not end_date:
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = today
        else:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # الحصول على الإيرادات والمصروفات اليومية
        from django.db.models.functions import TruncDate
        
        # ✅ الإيرادات من المدفوعات
        daily_income = Payment.objects.filter(
            payment_date__range=[start_date, end_date],
            status=Payment.Status.PAID
        ).annotate(date=TruncDate('payment_date')).values('date').annotate(
            total=Sum('amount')
        ).order_by('date')
        
        daily_expenses = Expense.objects.filter(
            expense_date__range=[start_date, end_date],
            status=Expense.Status.PAID
        ).annotate(date=TruncDate('expense_date')).values('date').annotate(
            total=Sum('amount')
        ).order_by('date')
        
        # دمج البيانات
        cash_flow_data = []
        dates = set()
        for item in daily_income:
            dates.add(item['date'])
        for item in daily_expenses:
            dates.add(item['date'])
        
        for date in sorted(dates):
            income = next((item['total'] for item in daily_income if item['date'] == date), 0)
            expenses = next((item['total'] for item in daily_expenses if item['date'] == date), 0)
            cash_flow_data.append({
                'date': date,
                'income': income,
                'expenses': expenses,
                'net': income - expenses,
            })
        
        return Response(cash_flow_data)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔹 Balance Sheet
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @action(detail=False, methods=['get'])
    def balance_sheet(self, request):
        """الميزانية العمومية"""
        from datetime import datetime
        
        date = request.query_params.get('date', timezone.now().date())
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # ✅ الإيرادات من المدفوعات حتى التاريخ
        total_income = Payment.objects.filter(
            payment_date__lte=date,
            status=Payment.Status.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # المصروفات حتى التاريخ
        total_expenses = Expense.objects.filter(
            expense_date__lte=date,
            status=Expense.Status.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # الربح التراكمي
        accumulated_profit = total_income - total_expenses
        
        # الإيرادات والمصروفات الشهرية
        monthly_income = Payment.objects.filter(
            payment_date__year=date.year,
            payment_date__month=date.month,
            status=Payment.Status.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_expenses = Expense.objects.filter(
            expense_date__year=date.year,
            expense_date__month=date.month,
            status=Expense.Status.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'date': date,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'accumulated_profit': accumulated_profit,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'monthly_profit': monthly_income - monthly_expenses,
        })