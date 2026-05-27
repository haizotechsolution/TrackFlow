from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import DailyAnalytics
from .serializers import DailyAnalyticsSerializer
from .services import build_admin_csv_response, build_user_pdf_response
from apps.shipments.models import DELIVERED, FAILED, RTO, Shipment


class MerchantAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = getattr(request.user, 'merchant_profile', None)
        if merchant is None:
            return Response(
                {'detail': 'Merchant profile not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        analytics = DailyAnalytics.objects.filter(
            merchant=merchant
        )[:30]

        serializer = DailyAnalyticsSerializer(analytics, many=True)

        return Response(serializer.data)


@login_required(login_url='account-login-page')
def merchant_dashboard_page(request):
    shipments = Shipment.objects.select_related('merchant')

    if request.user.is_authenticated and not (
        request.user.is_staff or getattr(request.user, 'is_ops', False)
    ):
        shipments = shipments.filter(merchant=request.user)

    total_shipments = shipments.count()
    delivered_shipments = shipments.filter(status=DELIVERED).count()
    failed_shipments = shipments.filter(status=FAILED).count()
    rto_shipments = shipments.filter(status=RTO).count()
    total_revenue = shipments.aggregate(total=Sum('freight_amount'))['total'] or 0

    context = {
        'total_shipments': total_shipments,
        'delivered_shipments': delivered_shipments,
        'failed_shipments': failed_shipments,
        'rto_shipments': rto_shipments,
        'total_revenue': total_revenue,
    }

    return render(request, 'merchant/dashboard.html', context)


class AdminAnalyticsCSVReportView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, period):
        if not (request.user.is_staff or getattr(request.user, 'is_ops', False)):
            return Response({'detail': 'Admin report access is not allowed.'}, status=403)

        try:
            return build_admin_csv_response(request.user, period)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)


class UserAnalyticsPDFReportView(APIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, period):
        if request.user.is_staff or getattr(request.user, 'is_ops', False):
            return Response({'detail': 'Use admin CSV reports for platform analytics.'}, status=400)

        try:
            return build_user_pdf_response(request.user, period)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
