from django.contrib import admin
from django.http import HttpResponse
import csv

from .models import Address, Shipment, ShipmentItem


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'city', 'state', 'pincode')
    search_fields = ('name', 'phone', 'city', 'pincode')


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('awb', 'merchant', 'receiver_address', 'service_type', 'status', 'created_at')
    list_filter = ('status', 'service_type', 'is_reverse', 'is_fragile')
    search_fields = ('awb', 'merchant__email', 'receiver_address__name', 'receiver_address__pincode')
    actions = ['export_to_csv', 'bulk_mark_pickup_scheduled']

    @admin.action(description='Export selected shipments to CSV')
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="shipments.csv"'
        writer = csv.writer(response)
        writer.writerow(['AWB', 'Merchant', 'Status', 'Service', 'COD', 'Created'])
        for shipment in queryset:
            writer.writerow([
                shipment.awb,
                shipment.merchant.email if shipment.merchant else '',
                shipment.status,
                shipment.service_type,
                shipment.cod_amount,
                shipment.created_at,
            ])
        return response

    @admin.action(description='Bulk mark pickup scheduled')
    def bulk_mark_pickup_scheduled(self, request, queryset):
        updated = 0
        for shipment in queryset:
            if shipment.status == 'BOOKED':
                shipment.schedule_pickup()
                shipment.save()
                updated += 1
        self.message_user(request, f'{updated} shipment(s) marked pickup scheduled.')


@admin.register(ShipmentItem)
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'name', 'quantity', 'declared_value', 'hsn_code')
