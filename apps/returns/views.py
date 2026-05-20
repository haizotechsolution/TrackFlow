from rest_framework import viewsets

from django.shortcuts import render

from .models import *

from .serializers import *


class ReturnViewSet(
viewsets.ModelViewSet
):

    queryset=ReturnRequest.objects.all()

    serializer_class=ReturnSerializer


def ndr_page(request):

    returns=ReturnRequest.objects.all()

    return render(
        request,
        "returns/ndr_list.html",
        {
            "returns":returns
        }
    )


def ndr_ops_page(request):

    return render(
        request,
        "returns/ndr_ops.html"
    )