from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, IncomeViewSet, FinanceViewSet

router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expenses')
router.register(r'incomes', IncomeViewSet, basename='incomes')
router.register(r'finance', FinanceViewSet, basename='finance')

urlpatterns = [
    path('', include(router.urls)),
]