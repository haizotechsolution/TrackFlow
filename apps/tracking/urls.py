from django.urls import path

from .views import (
    TrackingEventListCreateView,
    TrackingLocationListCreateView,
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
]
