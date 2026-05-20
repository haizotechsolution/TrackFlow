from rest_framework import serializers
from .models import *


class RateCardSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = RateCard
        fields = "__all__"


class InvoiceSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Invoice
        fields = "__all__"


class CODSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = CODRemittance
        fields = "__all__"