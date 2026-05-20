from django.urls import path

from .views import (
    TrackingEventListCreateView,
    TrackingLocationListCreateView,
    ShipmentTrackingTimelineView,
    LatestShipmentTrackingView,
)

urlpatterns = [

    path(
        'events/',
        TrackingEventListCreateView.as_view(),
        name='tracking-events',
    ),

    path(
        'locations/',
        TrackingLocationListCreateView.as_view(),
        name='tracking-locations',
    ),

    path(
    'timeline/<str:tracking_number>/',
    ShipmentTrackingTimelineView.as_view(),
    name='tracking-timeline',
    ),

    path(
    'latest/<str:tracking_number>/',
    LatestShipmentTrackingView.as_view(),
    name='latest-tracking',
    ),
]
