from rest_framework.routers import DefaultRouter

from django.urls import path

from .views import *

router=DefaultRouter()

router.register(
"ndr",
ReturnViewSet
)

urlpatterns=router.urls

urlpatterns += [

path(
"page/ndr/",
ndr_page
),

path(
"page/ops/",
ndr_ops_page
),

]