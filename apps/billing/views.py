from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.shipments.models import Shipment
from apps.shipments.services import calculate_freight_amount

from .models import Invoice
from .serializers import InvoiceSerializer
from .services import calculate_gst


class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Invoice.objects.all().order_by('-created_at')
        user = self.request.user
        if user.is_staff or getattr(user, 'is_ops', False):
            return queryset
        return queryset.filter(merchant_id=user.id)

    def perform_create(self, serializer):
        merchant_id = self.request.user.id
        if self.request.user.is_staff or getattr(self.request.user, 'is_ops', False):
            merchant_id = serializer.validated_data.get('merchant_id', merchant_id)
        serializer.save(merchant_id=merchant_id)


class BillingInvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "billing/invoice_list.html"
    context_object_name = "invoices"
    login_url = 'account-login-page'
    paginate_by = 25

    def get_queryset(self):
        queryset = Invoice.objects.all().order_by('-created_at')
        user = self.request.user
        if user.is_staff or getattr(user, 'is_ops', False):
            return queryset
        return queryset.filter(merchant_id=user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shipments"] = self.get_billable_shipments()
        return context

    def post(self, request, *args, **kwargs):
        shipment_awb = request.POST.get("shipment_awb", "").strip()
        shipment = get_object_or_404(
            self.get_billable_shipments(limit=False),
            awb=shipment_awb,
        )
        amount = shipment.freight_amount or calculate_freight_amount(
            shipment.weight_kg,
            shipment.length_cm,
            shipment.width_cm,
            shipment.height_cm,
            shipment.service_type,
            shipment.cod_amount,
        )
        gst_amount = calculate_gst(amount)
        invoice = Invoice.objects.create(
            merchant_id=shipment.merchant_id or request.user.id,
            invoice_number=self.generate_invoice_number(shipment),
            total_amount=amount,
            gst_amount=gst_amount,
            grand_total=amount + gst_amount,
        )
        return redirect(reverse("billing-invoice-detail", kwargs={"pk": invoice.pk}))

    def get_billable_shipments(self, limit=True):
        queryset = Shipment.objects.select_related(
            "sender_address",
            "receiver_address",
            "merchant",
        ).order_by("-created_at")
        user = self.request.user
        if not user.is_staff and not getattr(user, "is_ops", False):
            queryset = queryset.filter(merchant=user)
        if limit:
            return queryset[:25]
        return queryset

    def generate_invoice_number(self, shipment):
        date_part = timezone.now().strftime("%Y%m%d")
        prefix = f"INV-{date_part}-{shipment.awb}"
        sequence = Invoice.objects.filter(invoice_number__startswith=prefix).count() + 1
        return f"{prefix}-{sequence:04d}"


class BillingInvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = "billing/invoice_detail.html"
    context_object_name = "invoice"
    login_url = 'account-login-page'

    def get_queryset(self):
        queryset = Invoice.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, 'is_ops', False):
            return queryset
        return queryset.filter(merchant_id=user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.object
        parts = invoice.invoice_number.split("-")
        awb = parts[2] if len(parts) >= 3 else ""
        shipment_queryset = Shipment.objects.select_related(
            "sender_address",
            "receiver_address",
            "merchant",
        )
        user = self.request.user
        if not user.is_staff and not getattr(user, "is_ops", False):
            shipment_queryset = shipment_queryset.filter(merchant=user)
        context["shipment"] = shipment_queryset.filter(awb=awb).first()
        return context
