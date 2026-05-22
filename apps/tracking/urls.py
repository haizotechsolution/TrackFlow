from django.urls import path

from .views import (
    tracking_page,
    TrackingEventListCreateView,
    TrackingLocationListCreateView,
    ShipmentTrackingTimelineView,
    LatestShipmentTrackingView,
)

urlpatterns = [
    path(
        'page/',
        tracking_page,
        name='tracking-page',
    ),

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
    'timeline/<str:awb>/',
    ShipmentTrackingTimelineView.as_view(),
    name='tracking-timeline',
    ),

    path(
    'latest/<str:awb>/',
    LatestShipmentTrackingView.as_view(),
    name='latest-tracking',
    ),
]
