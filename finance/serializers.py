from rest_framework import serializers
from django.db.models import Sum
from .models import Expense, Income


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 EXPENSE SERIALIZERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ExpenseListSerializer(serializers.ModelSerializer):
    """Serializers لعرض المصروفات (خفيف)"""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'amount', 'category', 'category_display',
            'status', 'status_display', 'payment_method', 'payment_method_display',
            'expense_date', 'is_overdue', 'created_at'
        ]


class ExpenseDetailSerializer(serializers.ModelSerializer):
    """Serializers لعرض تفاصيل المصروف (كامل)"""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    booking_title = serializers.CharField(source='booking.title', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    is_paid = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'description', 'amount', 'category', 'category_display',
            'payment_method', 'payment_method_display', 'status', 'status_display',
            'project', 'project_name', 'booking', 'booking_title',
            'receipt', 'receipt_number',
            'vendor', 'vendor_phone',
            'expense_date', 'due_date', 'paid_date',
            'created_at', 'updated_at',
            'created_by', 'created_by_name',
            'is_paid', 'is_pending', 'is_overdue'
        ]
        read_only_fields = ['created_at', 'updated_at', 'paid_date']


class ExpenseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializers لإنشاء وتحديث المصروفات"""
    
    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'description', 'amount', 'category',
            'payment_method', 'status',
            'project', 'booking',
            'receipt', 'receipt_number',
            'vendor', 'vendor_phone',
            'expense_date', 'due_date',
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('المبلغ يجب أن يكون أكبر من صفر')
        return value
    
    def validate(self, data):
        if data.get('due_date') and data.get('expense_date'):
            if data['due_date'] < data['expense_date']:
                raise serializers.ValidationError({
                    'due_date': 'تاريخ الاستحقاق لا يمكن أن يكون قبل تاريخ المصروف'
                })
        return data


class ExpenseBulkCreateSerializer(serializers.Serializer):
    """Serializers لإنشاء مصروفات متعددة"""
    
    expenses = ExpenseCreateUpdateSerializer(many=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 INCOME SERIALIZERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class IncomeListSerializer(serializers.ModelSerializer):
    """Serializers لعرض الإيرادات (خفيف)"""
    
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Income
        fields = [
            'id', 'title', 'amount', 'source', 'source_display',
            'payment_method', 'payment_method_display',
            'income_date', 'created_at'
        ]


class IncomeDetailSerializer(serializers.ModelSerializer):
    """Serializers لعرض تفاصيل الإيراد (كامل)"""
    
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    booking_customer = serializers.CharField(source='booking.customer.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    is_from_booking = serializers.ReadOnlyField()
    
    class Meta:
        model = Income
        fields = [
            'id', 'title', 'amount', 'source', 'source_display',
            'payment_method', 'payment_method_display',
            'booking', 'booking_customer', 'customer', 'customer_name',
            'project', 'project_name',
            'invoice_number', 'invoice_file',
            'description', 'notes',
            'income_date',
            'created_at', 'updated_at',
            'created_by', 'created_by_name',
            'is_from_booking'
        ]
        read_only_fields = ['created_at', 'updated_at']


class IncomeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializers لإنشاء وتحديث الإيرادات"""
    
    class Meta:
        model = Income
        fields = [
            'id', 'title', 'amount', 'source', 'payment_method',
            'booking', 'customer', 'project',
            'invoice_number', 'invoice_file',
            'description', 'notes',
            'income_date',
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('المبلغ يجب أن يكون أكبر من صفر')
        return value
    
    def validate(self, data):
        # التحقق من أن الحجز والعميل متناسقين إن وجدا
        if data.get('booking') and data.get('customer'):
            if data['booking'].customer != data['customer']:
                raise serializers.ValidationError({
                    'customer': 'العميل لا يتطابق مع الحجز المحدد'
                })
        return data


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔹 FINANCE REPORT SERIALIZERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class FinanceSummarySerializer(serializers.Serializer):
    """Serializers للملخص المالي"""
    
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    income_count = serializers.IntegerField()
    expense_count = serializers.IntegerField()
    
    income_by_source = serializers.DictField()
    expenses_by_category = serializers.DictField()


class FinanceMonthlySerializer(serializers.Serializer):
    """Serializers للتقرير الشهري"""
    
    month = serializers.CharField()
    year = serializers.IntegerField()
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2)


class FinanceYearlySerializer(serializers.Serializer):
    """Serializers للتقرير السنوي"""
    
    year = serializers.IntegerField()
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_data = FinanceMonthlySerializer(many=True)