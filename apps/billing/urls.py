from django.urls import path
from .views import BillingInvoiceDetailView, BillingInvoiceListView, InvoiceListCreateView

urlpatterns = [
    path("", BillingInvoiceListView.as_view(), name="billing-invoice-list"),
    path("invoice/<int:pk>/", BillingInvoiceDetailView.as_view(), name="billing-invoice-detail"),
    path("invoices/", InvoiceListCreateView.as_view()),
]
