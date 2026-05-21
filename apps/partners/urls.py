from django.urls import path

from .views import CarrierListCreateView

urlpatterns = [
    path('carriers/', CarrierListCreateView.as_view()),
]