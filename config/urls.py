from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import TrackFlowTokenObtainPairView


def home(request):
    return HttpResponse("TrackFlow API running")


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/token/", TrackFlowTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/", include("apps.shipments.urls")),
    path("api/billing/", include("apps.billing.urls")),
    path("api/returns/", include("apps.returns.urls")),
]
