from django.urls import path
from .views import (
    MerchantAnalyticsAPIView,
    merchant_dashboard_page,
)

urlpatterns = [
    path('merchant/', MerchantAnalyticsAPIView.as_view(), name='merchant_analytics_api'),
    path('dashboard/', merchant_dashboard_page, name='merchant_dashboard'),
]
