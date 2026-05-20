from rest_framework import serializers
from .models import *


class ReturnSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = ReturnRequest
        fields = "__all__"