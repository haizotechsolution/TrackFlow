from rest_framework import serializers

from .models import Carrier, CarrierWebhookLog


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = '__all__'


class CarrierWebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierWebhookLog
        fields = '__all__'