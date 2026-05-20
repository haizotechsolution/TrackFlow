from rest_framework import serializers
from .models import DailyAnalytics


class DailyAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAnalytics
        fields = '__all__'