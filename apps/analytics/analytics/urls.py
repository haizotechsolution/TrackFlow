from django.urls import path
from .views import (
    MerchantAnalyticsAPIView,
    MerchantDashboardView
)

urlpatterns = [
    path('merchant/', MerchantAnalyticsAPIView.as_view(), name='merchant_analytics_api'),
    path('dashboard/', MerchantDashboardView.as_view(), name='merchant_dashboard'),
]
