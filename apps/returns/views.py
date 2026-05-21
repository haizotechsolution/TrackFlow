from rest_framework import generics
from .models import NDR
from .serializers import NDRSerializer


class NDRListCreateView(generics.ListCreateAPIView):
    queryset = NDR.objects.all()
    serializer_class = NDRSerializer