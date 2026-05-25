from rest_framework import serializers
from .models import TrackingEvent, TrackingLocation


def validate_shipment_access(serializer, shipment):
    request = serializer.context.get('request')
    if not request or not request.user.is_authenticated:
        raise serializers.ValidationError('Authentication is required.')
    if request.user.is_staff or getattr(request.user, 'is_ops', False):
        return shipment
    if shipment.merchant_id != request.user.id:
        raise serializers.ValidationError('You cannot update tracking for this shipment.')
    return shipment


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

    def validate_shipment(self, shipment):
        return validate_shipment_access(self, shipment)

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

    def validate_shipment(self, shipment):
        return validate_shipment_access(self, shipment)
