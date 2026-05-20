from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    BulkShipmentCreateView,
    ShipmentViewSet,
    bulk_upload_page,
    shipment_create_page,
    shipment_detail_page,
    shipment_label_page,
    shipment_list_page,
)

router = DefaultRouter()
router.register(r'shipments', ShipmentViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('shipments/bulk/', BulkShipmentCreateView.as_view(), name='shipment-bulk-create'),
    path('shipments/page/', shipment_list_page, name='shipment-list-page'),
    path('shipments/page/new/', shipment_create_page, name='shipment-create-page'),
    path('shipments/page/bulk-upload/', bulk_upload_page, name='shipment-bulk-upload-page'),
    path('shipments/page/<str:awb>/', shipment_detail_page, name='shipment-detail-page'),
    path('shipments/page/<str:awb>/label/', shipment_label_page, name='shipment-label-page'),
]
