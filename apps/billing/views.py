from rest_framework import viewsets

from django.shortcuts import render,get_object_or_404

from .models import *

from .serializers import *


class RateCardViewSet(
viewsets.ModelViewSet
):

    queryset=RateCard.objects.all()

    serializer_class=RateCardSerializer


class InvoiceViewSet(
viewsets.ModelViewSet
):

    queryset=Invoice.objects.all()

    serializer_class=InvoiceSerializer


class CODViewSet(
viewsets.ModelViewSet
):

    queryset=CODRemittance.objects.all()

    serializer_class=CODSerializer


def ratecard_page(request):

    ratecards=RateCard.objects.all()

    return render(
        request,
        "billing/rate_card_list.html",
        {
            "ratecards":ratecards
        }
    )


def invoice_page(request):

    invoices=Invoice.objects.all()

    return render(
        request,
        "billing/invoice_list.html",
        {
            "invoices":invoices
        }
    )


def invoice_detail_page(
request,
pk
):

    invoice=get_object_or_404(
        Invoice,
        id=pk
    )

    return render(
        request,
        "billing/invoice_detail.html",
        {
            "invoice":invoice
        }
    )


def cod_page(request):

    cods=CODRemittance.objects.all()

    return render(
        request,
        "billing/cod_remittance.html",
        {
            "cods":cods
        }
    )