from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from apps.accounts.views import (
    TrackFlowTokenObtainPairView
)


def health_check(request):

    return JsonResponse({
        'status': 'ok',
        'db': 'ok',
        'redis': 'skipped',
        'celery': 'skipped'
    })


urlpatterns = [

    path('admin/', admin.site.urls),

    # JWT Authentication
    path(
        'api/token/',
        TrackFlowTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    # Health Check
    path(
        'health/',
        health_check,
        name='health-check'
    ),

    # Tracking APIs
    path(
        'api/tracking/',
        include('apps.tracking.urls')
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

    # Accounts APIs
    path(
        'api/accounts/',
        include('apps.accounts.urls')
    ),
]

urlpatterns += [
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/partners/', include('apps.partners.urls')),
]
