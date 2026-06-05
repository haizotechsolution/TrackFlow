from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from rest_framework import generics

from .models import TrackingEvent, TrackingLocation

from .serializers import (
    TrackingEventSerializer,
    TrackingLocationSerializer,
)
from rest_framework.permissions import (
    IsAuthenticated
)

TRACKFLOW_HUBS = [
    {
        "name": "TrackFlow Chennai Hub",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "code": "TF-MAA",
        "contact": "+91 44 4000 1101",
        "status": "Active",
        "lat": 13.0827,
        "lng": 80.2707,
    },
    {
        "name": "TrackFlow Coimbatore Hub",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "code": "TF-CJB",
        "contact": "+91 422 400 2102",
        "status": "Active",
        "lat": 11.0168,
        "lng": 76.9558,
    },
    {
        "name": "TrackFlow Madurai Hub",
        "city": "Madurai",
        "state": "Tamil Nadu",
        "code": "TF-IXM",
        "contact": "+91 452 400 3103",
        "status": "Active",
        "lat": 9.9252,
        "lng": 78.1198,
    },
    {
        "name": "TrackFlow Trichy Hub",
        "city": "Trichy",
        "state": "Tamil Nadu",
        "code": "TF-TRZ",
        "contact": "+91 431 400 4104",
        "status": "Active",
        "lat": 10.7905,
        "lng": 78.7047,
    },
    {
        "name": "TrackFlow Salem Hub",
        "city": "Salem",
        "state": "Tamil Nadu",
        "code": "TF-SXM",
        "contact": "+91 427 400 5105",
        "status": "Active",
        "lat": 11.6643,
        "lng": 78.1460,
    },
    {
        "name": "TrackFlow Tirunelveli Hub",
        "city": "Tirunelveli",
        "state": "Tamil Nadu",
        "code": "TF-TEN",
        "contact": "+91 462 400 6106",
        "status": "Active",
        "lat": 8.7139,
        "lng": 77.7567,
    },
    {
        "name": "TrackFlow Erode Hub",
        "city": "Erode",
        "state": "Tamil Nadu",
        "code": "TF-ED",
        "contact": "+91 424 400 7107",
        "status": "Active",
        "lat": 11.3410,
        "lng": 77.7172,
    },
    {
        "name": "TrackFlow Vellore Hub",
        "city": "Vellore",
        "state": "Tamil Nadu",
        "code": "TF-VLR",
        "contact": "+91 416 400 8108",
        "status": "Active",
        "lat": 12.9165,
        "lng": 79.1325,
    },
    {
        "name": "TrackFlow Tiruppur Hub",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "code": "TF-TUP",
        "contact": "+91 421 400 9109",
        "status": "Active",
        "lat": 11.1085,
        "lng": 77.3411,
    },
    {
        "name": "TrackFlow Thanjavur Hub",
        "city": "Thanjavur",
        "state": "Tamil Nadu",
        "code": "TF-TJV",
        "contact": "+91 4362 400 111",
        "status": "Active",
        "lat": 10.7867,
        "lng": 79.1378,
    },
    {
        "name": "TrackFlow Bengaluru Hub",
        "city": "Bengaluru",
        "state": "Karnataka",
        "code": "TF-BLR",
        "contact": "+91 80 4000 1212",
        "status": "Active",
        "lat": 12.9716,
        "lng": 77.5946,
    },
    {
        "name": "TrackFlow Hyderabad Hub",
        "city": "Hyderabad",
        "state": "Telangana",
        "code": "TF-HYD",
        "contact": "+91 40 4000 1313",
        "status": "Active",
        "lat": 17.3850,
        "lng": 78.4867,
    },
    {
        "name": "TrackFlow Kochi Hub",
        "city": "Kochi",
        "state": "Kerala",
        "code": "TF-COK",
        "contact": "+91 484 400 1414",
        "status": "Active",
        "lat": 9.9312,
        "lng": 76.2673,
    },
    {
        "name": "TrackFlow Mysuru Hub",
        "city": "Mysuru",
        "state": "Karnataka",
        "code": "TF-MYS",
        "contact": "+91 821 400 1515",
        "status": "Active",
        "lat": 12.2958,
        "lng": 76.6394,
    },
    {
        "name": "TrackFlow Vijayawada Hub",
        "city": "Vijayawada",
        "state": "Andhra Pradesh",
        "code": "TF-VGA",
        "contact": "+91 866 400 1616",
        "status": "Active",
        "lat": 16.5062,
        "lng": 80.6480,
    },
]


def scoped_tracking_events(user):
    queryset = TrackingEvent.objects.select_related(
        'shipment',
        'shipment__sender_address',
        'shipment__receiver_address',
        'shipment__merchant',
    )
    if user.is_staff or getattr(user, 'is_ops', False):
        return queryset
    return queryset.filter(shipment__merchant=user)


def scoped_tracking_locations(user):
    queryset = TrackingLocation.objects.select_related('shipment', 'shipment__merchant')
    if user.is_staff or getattr(user, 'is_ops', False):
        return queryset
    return queryset.filter(shipment__merchant=user)


@login_required(login_url='account-login-page')
def tracking_page(request):
    events = (
        scoped_tracking_events(request.user)
        .order_by('-event_time')[:50]
    )
    return render(
        request,
        'tracking/tracking_list.html',
        {
            'events': events,
            'hub_locations': TRACKFLOW_HUBS,
            'hub_cities': sorted({hub["city"] for hub in TRACKFLOW_HUBS}),
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        },
    )


class TrackingEventListCreateView(
    generics.ListCreateAPIView
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = scoped_tracking_events(self.request.user).order_by('-event_time')
        shipment_id = self.request.query_params.get('shipment')

        if shipment_id:

            queryset = queryset.filter(
                shipment_id=shipment_id
            )

        return queryset


    serializer_class = TrackingEventSerializer


class TrackingLocationListCreateView(
    generics.ListCreateAPIView
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = scoped_tracking_locations(self.request.user).order_by('-recorded_at')

        shipment_id = self.request.query_params.get('shipment')

        if shipment_id:

            queryset = queryset.filter(
                shipment_id=shipment_id
            )

        return queryset

    serializer_class = TrackingLocationSerializer


class ShipmentTrackingTimelineView(
    generics.ListAPIView
):
    permission_classes = [IsAuthenticated]
    serializer_class = TrackingEventSerializer

    def get_queryset(self):
        awb = self.kwargs.get('awb')
        return scoped_tracking_events(self.request.user).filter(
            shipment__awb=awb
        ).order_by('-event_time')


class LatestShipmentTrackingView(
    generics.RetrieveAPIView
):
    permission_classes = [IsAuthenticated]
    serializer_class = TrackingEventSerializer

    def get_object(self):
        awb = self.kwargs.get('awb')
        return get_object_or_404(
            scoped_tracking_events(self.request.user).order_by('-event_time'),
            shipment__awb=awb,
        )
