from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import render

from .models import WebhookEndpoint
from .serializers import (
    ProfileSerializer,
    RegisterSerializer,
    TrackFlowTokenObtainPairSerializer,
    WebhookEndpointSerializer,
)


class TrackFlowTokenObtainPairView(TokenObtainPairView):
    serializer_class = TrackFlowTokenObtainPairSerializer


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
        if not refresh:
            return Response({'detail': 'Refresh token is required.'}, status=400)

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


def settings_page(request):
    return render(request, 'accounts/settings.html')
