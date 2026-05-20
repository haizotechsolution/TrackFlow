from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ShipmentFilter
from .models import Shipment
from .serializers import ShipmentSerializer
from .services import bulk_create_shipments_from_csv, generate_label_pdf, get_pod_upload_url


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'awb'
    filterset_class = ShipmentFilter
    search_fields = ['awb', 'receiver_address__name', 'receiver_address__phone']
    ordering_fields = ['created_at', 'updated_at', 'status']

    def get_permissions(self):
        if self.action == 'retrieve':
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = Shipment.objects.select_related('sender_address', 'receiver_address', 'merchant').prefetch_related('items')
        if not user.is_authenticated:
            return queryset
        if user.is_staff or getattr(user, 'is_ops', False):
            return queryset
        return queryset.filter(merchant=user)

    @action(detail=True, methods=['get'], url_path='label')
    def label(self, request, awb=None):
        shipment = self.get_object()
        pdf = generate_label_pdf(shipment.id)
        return FileResponse(pdf, content_type='application/pdf', filename=f'{shipment.awb}.pdf')

    @action(detail=True, methods=['post'], url_path='pod-upload-url')
    def pod_upload_url(self, request, awb=None):
        shipment = self.get_object()
        return Response(get_pod_upload_url(shipment.awb))


class BulkShipmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'detail': 'CSV file is required.'}, status=400)
        return Response(bulk_create_shipments_from_csv(csv_file, request.user))


def shipment_list_page(request):
    shipments = Shipment.objects.select_related('receiver_address').order_by('-created_at')[:50]
    return render(request, 'shipments/shipment_list.html', {'shipments': shipments})


def shipment_detail_page(request, awb):
    shipment = get_object_or_404(Shipment.objects.select_related('sender_address', 'receiver_address'), awb=awb)
    return render(request, 'shipments/shipment_detail.html', {'shipment': shipment})


def shipment_create_page(request):
    return render(request, 'shipments/shipment_create.html')


def bulk_upload_page(request):
    return render(request, 'shipments/bulk_upload.html')


def shipment_label_page(request, awb):
    shipment = get_object_or_404(Shipment.objects.select_related('sender_address', 'receiver_address'), awb=awb)
    return render(request, 'shipments/label.html', {'shipment': shipment})
