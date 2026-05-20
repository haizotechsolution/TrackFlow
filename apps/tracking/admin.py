from django.contrib import admin
from .models import TrackingEvent, TrackingLocation

@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):

    list_display = (
        'shipment',
        'status',
        'location',
        'event_time',
    )

    search_fields = (
        'shipment__awb_number',
        'status',
        'location',
    )

    list_filter = (
        'status',
        'event_time',
    )

    ordering = ('-event_time',)


@admin.register(TrackingLocation)
class TrackingLocationAdmin(admin.ModelAdmin):

    list_display = (
        'shipment',
        'latitude',
        'longitude',
        'recorded_at',
    )

    search_fields = (
        'shipment__awb_number',
    )

    list_filter = (
        'recorded_at',
    )

    ordering = ('-recorded_at',)