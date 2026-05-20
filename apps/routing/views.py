from rest_framework import generics

from .models import Route
from .serializers import RouteSerializer


class RouteListCreateView(
    generics.ListCreateAPIView
):

    queryset = Route.objects.all().order_by(
        '-created_at'
    )

    serializer_class = RouteSerializer


class RouteDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Route.objects.all()

    serializer_class = RouteSerializer