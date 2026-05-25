from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Invoice
from .serializers import InvoiceSerializer


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
