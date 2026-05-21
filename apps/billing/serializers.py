from rest_framework import serializers
from .models import Invoice, RateCard, CODRemittance


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class RateCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateCard
        fields = "__all__"


class CODRemittanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CODRemittance
        fields = "__all__"