from django.contrib import admin
from .models import DailyAnalytics


@admin.register(DailyAnalytics)
class DailyAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        'merchant',
        'analytics_date',
        'total_shipments',
        'delivered_shipments',
        'failed_shipments',
        'total_revenue'
    )

    search_fields = ('merchant__company_name',)
    list_filter = ('analytics_date',)