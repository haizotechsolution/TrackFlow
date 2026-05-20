from rest_framework import generics

from .models import TrackingEvent, TrackingLocation

from .serializers import (
    TrackingEventSerializer,
    TrackingLocationSerializer,
)


class TrackingEventListCreateView(
    generics.ListCreateAPIView
):

    queryset = TrackingEvent.objects.all()

    serializer_class = TrackingEventSerializer


class TrackingLocationListCreateView(
    generics.ListCreateAPIView
):

    queryset = TrackingLocation.objects.all()

    serializer_class = TrackingLocationSerializer