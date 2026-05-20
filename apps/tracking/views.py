from rest_framework import generics

from .models import TrackingEvent, TrackingLocation

from .serializers import (
    TrackingEventSerializer,
    TrackingLocationSerializer,
)
from rest_framework.permissions import (
    IsAuthenticated
)


class TrackingEventListCreateView(
    generics.ListCreateAPIView
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = TrackingEvent.objects.all().order_by(
    '-event_time'
)
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

        queryset = TrackingLocation.objects.all().order_by(
    '-recorded_at'
)

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

        tracking_number = self.kwargs.get(
            'tracking_number'
        )

        return TrackingEvent.objects.filter(
            shipment__tracking_number=tracking_number
        ).order_by('-event_time')


class LatestShipmentTrackingView(
    generics.RetrieveAPIView
):
    permission_classes = [IsAuthenticated]
    serializer_class = TrackingEventSerializer

    def get_object(self):

        tracking_number = self.kwargs.get(
            'tracking_number'
        )

        return TrackingEvent.objects.filter(
            shipment__tracking_number=tracking_number
        ).order_by('-event_time').first()