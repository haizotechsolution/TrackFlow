from django.urls import path
from .views import test_api, protected_test

urlpatterns = [
    path('test/', test_api),
    path('protected/', protected_test),
]