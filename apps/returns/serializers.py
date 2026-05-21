from rest_framework import serializers
from .models import NDR


class NDRSerializer(serializers.ModelSerializer):
    class Meta:
        model = NDR
        fields = "__all__"