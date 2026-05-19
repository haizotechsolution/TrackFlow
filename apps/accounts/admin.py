from django.contrib import admin

from .models import CustomUser, Merchant

admin.site.register(CustomUser)

admin.site.register(Merchant)