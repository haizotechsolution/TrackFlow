from django.contrib import admin
from .models import RateCard, Invoice, CODRemittance

admin.site.register(RateCard)
admin.site.register(Invoice)
admin.site.register(CODRemittance)