from django.urls import path
from .views import BillingInvoiceListView, InvoiceListCreateView

urlpatterns = [
    path("", BillingInvoiceListView.as_view(), name="billing-invoice-list"),
    path("invoices/", InvoiceListCreateView.as_view()),
]
