from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import WebhookEndpoint
from .serializers import (
    ProfileSerializer,
    RegisterSerializer,
    TrackFlowTokenObtainPairSerializer,
    WebhookEndpointSerializer,
)


class TrackFlowTokenObtainPairView(TokenObtainPairView):
    serializer_class = TrackFlowTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        django_login(request._request, user)
        if not request.data.get('remember_me'):
            request._request.session.set_expiry(0)
        data = serializer.validated_data
        data["dashboard_url"] = get_dashboard_url(user)
        return Response(data, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(ProfileSerializer(user).data, status=201)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RotateAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        merchant = getattr(request.user, 'merchant_profile', None)
        if merchant is None:
            return Response({'detail': 'Merchant profile not found.'}, status=404)

        api_key = merchant.rotate_api_key()
        return Response({'api_key': str(api_key)})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get('refresh')
        django_logout(request)
        if not refresh:
            return Response(status=status.HTTP_204_NO_CONTENT)

        try:
            RefreshToken(refresh).blacklist()
        except AttributeError:
            return Response({'detail': 'Token blacklist app is not enabled.'}, status=501)
        except Exception:
            return Response({'detail': 'Invalid refresh token.'}, status=400)

        return Response(status=status.HTTP_204_NO_CONTENT)


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        merchant = getattr(self.request.user, 'merchant_profile', None)
        if merchant is None:
            return WebhookEndpoint.objects.none()
        return WebhookEndpoint.objects.filter(merchant=merchant, is_active=True)

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user.merchant_profile)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


def login_page(request):
    return render(request, 'accounts/login.html')


def register_page(request):
    return render(request, 'accounts/register.html')


@login_required(login_url='account-login-page')
def settings_page(request):
    return render(request, 'accounts/settings.html')


@require_POST
def web_logout(request):
    django_logout(request)
    return redirect('account-login-page')


def get_dashboard_url(user):
    if user.is_staff or getattr(user, 'is_ops', False):
        return reverse('home')
    if getattr(user, 'is_customer', False):
        return reverse('shipment-list-page')
    return reverse('merchant_dashboard')


def home_page(request):
    if not request.user.is_authenticated:
        return redirect('account-login-page')
    if request.user.is_authenticated and not (
        request.user.is_staff or getattr(request.user, 'is_ops', False)
    ):
        return redirect(get_dashboard_url(request.user))

    return render(request, 'admin.html')
