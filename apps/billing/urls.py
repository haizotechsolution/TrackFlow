from rest_framework.routers import DefaultRouter

from django.urls import path

from .views import *

router=DefaultRouter()

router.register(
"ratecards",
RateCardViewSet
)

router.register(
"invoices",
InvoiceViewSet
)

router.register(
"cod",
CODViewSet
)

urlpatterns=router.urls

urlpatterns += [

path(
"page/ratecards/",
ratecard_page
),

path(
"page/invoices/",
invoice_page
),

path(
"page/invoice/<int:pk>/",
invoice_detail_page
),

path(
"page/cod/",
cod_page
),

]