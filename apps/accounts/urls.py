from django.urls import path
from django.contrib.auth import views as auth_views
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
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/password_reset_email.html',
            success_url='/api/accounts/password-reset/done/',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/api/accounts/reset/done/',
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]

urlpatterns += router.urls
