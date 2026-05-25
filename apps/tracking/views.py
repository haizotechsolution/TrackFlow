from django.contrib.auth.decorators import login_required
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
    return render(request, 'tracking/tracking_list.html', {'events': events})


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
