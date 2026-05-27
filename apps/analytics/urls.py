from django.urls import path
from .views import (
    AdminAnalyticsCSVReportView,
    MerchantAnalyticsAPIView,
    UserAnalyticsPDFReportView,
    merchant_dashboard_page,
)

urlpatterns = [
    path('merchant/', MerchantAnalyticsAPIView.as_view(), name='merchant_analytics_api'),
    path('dashboard/', merchant_dashboard_page, name='merchant_dashboard'),
    path(
        'reports/admin/<str:period>/csv/',
        AdminAnalyticsCSVReportView.as_view(),
        name='admin-analytics-report-csv',
    ),
    path(
        'reports/<str:period>/pdf/',
        UserAnalyticsPDFReportView.as_view(),
        name='user-analytics-report-pdf',
    ),
]
