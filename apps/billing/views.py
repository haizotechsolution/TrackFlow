from rest_framework import generics
from django.views.generic import ListView
from .models import Invoice
from .serializers import InvoiceSerializer


class InvoiceListCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class BillingInvoiceListView(ListView):
    model = Invoice
    template_name = "billing/invoice_list.html"
    context_object_name = "invoices"
