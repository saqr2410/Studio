import django_filters
from .models import Booking

class BookingFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    status = django_filters.MultipleChoiceFilter(choices=Booking.STATUS_CHOICES)
    photographer = django_filters.NumberFilter(field_name='photographer__id')
    customer = django_filters.NumberFilter(field_name='customer__id')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    class Meta:
        model = Booking
        fields = ['date', 'status', 'photographer', 'customer', 'price']