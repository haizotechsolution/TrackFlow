from django.contrib import admin
from .models import ShipmentTransitEvent, TrackingEvent, TrackingLocation

@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):

    list_display = (
        'shipment',
        'status',
        'location',
        'event_time',
    )

    search_fields = (
        'shipment__awb',
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
        'shipment__awb',
    )

    list_filter = (
        'recorded_at',
    )

    ordering = ('-recorded_at',)


@admin.register(ShipmentTransitEvent)
class ShipmentTransitEventAdmin(admin.ModelAdmin):
    list_display = (
        'shipment',
        'event_type',
        'hub_name',
        'city',
        'event_timestamp',
        'created_at',
    )
    list_filter = (
        'event_type',
        'event_timestamp',
        'city',
    )
    search_fields = (
        'shipment__awb',
        'hub_name',
        'city',
        'remarks',
    )
    autocomplete_fields = ('shipment',)
    ordering = ('-event_timestamp',)
