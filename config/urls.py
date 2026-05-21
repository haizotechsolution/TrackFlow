from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include


def home(request):
    return HttpResponse("TrackFlow API running")


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/billing/", include("apps.billing.urls")),
    path("api/returns/", include("apps.returns.urls")),
]