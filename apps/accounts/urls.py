from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    LogoutView,
    ProfileView,
    RegisterView,
    RotateAPIKeyView,
    WebhookEndpointViewSet,
    login_page,
    register_page,
    settings_page,
    web_logout,
)

router = DefaultRouter()
router.register('webhooks', WebhookEndpointViewSet, basename='account-webhooks')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='account-register'),
    path('profile/', ProfileView.as_view(), name='account-profile'),
    path('api-key/rotate/', RotateAPIKeyView.as_view(), name='account-api-key-rotate'),
    path('logout/', LogoutView.as_view(), name='account-logout'),
    path('page/login/', login_page, name='account-login-page'),
    path('page/register/', register_page, name='account-register-page'),
    path('page/settings/', settings_page, name='account-settings-page'),
    path('page/logout/', web_logout, name='account-web-logout'),
]

urlpatterns += router.urls
