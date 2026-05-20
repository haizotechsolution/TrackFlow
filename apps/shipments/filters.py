import django_filters

from .models import Shipment


class ShipmentFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    city = django_filters.CharFilter(field_name='receiver_address__city', lookup_expr='icontains')
    awb = django_filters.CharFilter(field_name='awb', lookup_expr='icontains')

    class Meta:
        model = Shipment
        fields = ['status', 'service_type', 'date_from', 'date_to', 'city', 'awb']
