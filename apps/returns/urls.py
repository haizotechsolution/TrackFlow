from django.urls import path
from .views import NDRListCreateView

urlpatterns = [
    path("ndr/", NDRListCreateView.as_view()),
]