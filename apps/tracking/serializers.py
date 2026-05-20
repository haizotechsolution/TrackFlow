from rest_framework import serializers
from .models import TrackingEvent, TrackingLocation

class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingEvent

        fields = [
            'id',
            'shipment',
            'status',
            'description',
            'location',
            'event_time',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'event_time',
            'created_at',
        ]

class TrackingLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingLocation

        fields = [
            'id',
            'shipment',
            'latitude',
            'longitude',
            'recorded_at',
        ]

        read_only_fields = [
            'id',
            'recorded_at',
        ]