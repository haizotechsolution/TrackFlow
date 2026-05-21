from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from .models import Carrier
from .serializers import CarrierSerializer


class CarrierListCreateView(generics.ListCreateAPIView):
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer
    permission_classes = [IsAdminUser]