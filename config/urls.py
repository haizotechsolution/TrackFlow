from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Authentication
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    # Shipments APIs
    path(
        'api/',
        include('apps.shipments.urls')
    ),

    # Billing APIs
    path(
        'api/billing/',
        include('apps.billing.urls')
    ),

    # Returns APIs
    path(
        'api/returns/',
        include('apps.returns.urls')
    ),

    # Routing APIs
    path(
        'api/',
        include('apps.routing.urls')
    ),
]