from django.contrib import admin

from .models import CustomUser, Merchant, WebhookEndpoint


class MerchantInline(admin.StackedInline):
    model = Merchant
    can_delete = False
    extra = 0
    readonly_fields = ('api_key', 'created_at')


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'phone', 'is_merchant', 'is_ops', 'is_staff')
    list_filter = ('is_merchant', 'is_ops', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'phone')
    inlines = [MerchantInline]


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'url', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('merchant__company_name', 'url')

