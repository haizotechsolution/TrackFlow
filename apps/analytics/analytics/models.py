from django.db import models
from apps.accounts.models import Merchant


class DailyAnalytics(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)

    total_shipments = models.IntegerField(default=0)
    delivered_shipments = models.IntegerField(default=0)
    failed_shipments = models.IntegerField(default=0)
    rto_shipments = models.IntegerField(default=0)

    total_cod = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    analytics_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('merchant', 'analytics_date')
        ordering = ['-analytics_date']

    def __str__(self):
        return f"{self.merchant.company_name} - {self.analytics_date}"