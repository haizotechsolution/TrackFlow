from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import TrackFlowTokenObtainPairView, home_page


urlpatterns = [
    path("", home_page, name="home"),
    path("billing/", include("apps.billing.urls")),
    path("admin/", admin.site.urls),
    path("api/token/", TrackFlowTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/", include("apps.shipments.urls")),
    path("api/billing/", include("apps.billing.urls")),
    path("api/returns/", include("apps.returns.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/tracking/", include("apps.tracking.urls")),
    path("api/routing/", include("apps.routing.urls")),
    path("api/partners/", include("apps.partners.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
]
