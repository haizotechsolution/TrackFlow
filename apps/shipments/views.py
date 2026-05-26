from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django_fsm import can_proceed
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
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
    transition_actions = {
        'schedule_pickup': 'schedule_pickup',
        'mark_in_transit': 'mark_in_transit',
        'mark_out_for_delivery': 'mark_out_for_delivery',
        'mark_delivered': 'mark_delivered',
        'mark_failed': 'mark_failed',
        'mark_rto': 'mark_rto',
        'cancel': 'cancel',
    }

    def get_permissions(self):
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

    @action(detail=True, methods=['post'], url_path='transition')
    def transition_status(self, request, awb=None):
        shipment = self.get_object()
        action_name = request.data.get('action')
        method_name = self.transition_actions.get(action_name)
        if not method_name:
            return Response(
                {
                    'detail': 'Unsupported transition.',
                    'allowed_actions': list(self.transition_actions),
                },
                status=400,
            )

        transition_method = getattr(shipment, method_name)
        if not can_proceed(transition_method):
            return Response(
                {
                    'detail': (
                        f'Cannot run {action_name} while shipment '
                        f'is {shipment.status}.'
                    )
                },
                status=400,
            )

        transition_method()
        shipment.save(update_fields=['status', 'updated_at'])
        return Response(ShipmentSerializer(shipment).data)


class BulkShipmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'detail': 'CSV file is required.'}, status=400)
        return Response(bulk_create_shipments_from_csv(csv_file, request.user))


def scoped_shipments_for_user(user):
    queryset = Shipment.objects.select_related(
        'sender_address',
        'receiver_address',
        'merchant',
    ).prefetch_related('items')
    if user.is_staff or getattr(user, 'is_ops', False):
        return queryset
    return queryset.filter(merchant=user)


@login_required(login_url='account-login-page')
def shipment_list_page(request):
    shipments = scoped_shipments_for_user(request.user)
    search = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    city = request.GET.get('city', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if search:
        shipments = shipments.filter(awb__icontains=search)
    if status:
        shipments = shipments.filter(status=status)
    if city:
        shipments = shipments.filter(receiver_address__city__icontains=city)
    if date_from:
        shipments = shipments.filter(created_at__date__gte=date_from)
    if date_to:
        shipments = shipments.filter(created_at__date__lte=date_to)

    shipments = shipments.order_by('-created_at')[:100]
    return render(
        request,
        'shipments/shipment_list.html',
        {
            'shipments': shipments,
            'status_choices': Shipment.STATUS_CHOICES,
            'filters': request.GET,
        },
    )


@login_required(login_url='account-login-page')
def shipment_detail_page(request, awb):
    shipment = get_object_or_404(
        scoped_shipments_for_user(request.user).prefetch_related('tracking_events'),
        awb=awb,
    )
    return render(request, 'shipments/shipment_detail.html', {'shipment': shipment})


@login_required(login_url='account-login-page')
def shipment_create_page(request):
    if request.method == 'POST':
        data = {
            'sender_address': {
                'name': request.POST.get('sender_name', '').strip(),
                'phone': request.POST.get('sender_phone', '').strip(),
                'address_line_1': request.POST.get('sender_address_line_1', '').strip(),
                'address_line_2': request.POST.get('sender_address_line_2', '').strip(),
                'city': request.POST.get('sender_city', '').strip(),
                'state': request.POST.get('sender_state', '').strip(),
                'pincode': request.POST.get('sender_pincode', '').strip(),
                'landmark': request.POST.get('sender_landmark', '').strip(),
            },
            'receiver_address': {
                'name': request.POST.get('receiver_name', '').strip(),
                'phone': request.POST.get('receiver_phone', '').strip(),
                'address_line_1': request.POST.get('receiver_address_line_1', '').strip(),
                'address_line_2': request.POST.get('receiver_address_line_2', '').strip(),
                'city': request.POST.get('receiver_city', '').strip(),
                'state': request.POST.get('receiver_state', '').strip(),
                'pincode': request.POST.get('receiver_pincode', '').strip(),
                'landmark': request.POST.get('receiver_landmark', '').strip(),
            },
            'weight_kg': request.POST.get('weight_kg', '').strip(),
            'length_cm': request.POST.get('length_cm', '0').strip() or '0',
            'width_cm': request.POST.get('width_cm', '0').strip() or '0',
            'height_cm': request.POST.get('height_cm', '0').strip() or '0',
            'service_type': request.POST.get('service_type', Shipment.SERVICE_STANDARD),
            'cod_amount': request.POST.get('cod_amount', '0').strip() or '0',
            'is_fragile': request.POST.get('is_fragile') == 'on',
            'is_dangerous': request.POST.get('is_dangerous') == 'on',
            'is_reverse': request.POST.get('is_reverse') == 'on',
            'original_awb': request.POST.get('original_awb', '').strip(),
        }
        serializer = ShipmentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            shipment = serializer.save()
            return redirect('shipment-detail-page', awb=shipment.awb)
        return render(
            request,
            'shipments/shipment_create.html',
            {'errors': serializer.errors, 'form_data': request.POST},
            status=400
        )

    return render(request, 'shipments/shipment_create.html')


@login_required(login_url='account-login-page')
def bulk_upload_page(request):
    return render(request, 'shipments/bulk_upload.html')


@login_required(login_url='account-login-page')
def shipment_label_page(request, awb):
    shipment = get_object_or_404(scoped_shipments_for_user(request.user), awb=awb)
    return render(request, 'shipments/label.html', {'shipment': shipment})
