from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import DailyAnalytics
from .serializers import DailyAnalyticsSerializer


class MerchantAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = request.user.merchant

        analytics = DailyAnalytics.objects.filter(
            merchant=merchant
        )[:30]

        serializer = DailyAnalyticsSerializer(analytics, many=True)

        return Response(serializer.data)


class MerchantDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        analytics = DailyAnalytics.objects.filter(
            merchant=request.user.merchant
        ).first()

        context = {
            'analytics': analytics
        }

        return render(request, 'merchant/dashboard.html', context)
