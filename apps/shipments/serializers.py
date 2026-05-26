from rest_framework import serializers
from .models import Address, Shipment, ShipmentItem
from .services import calculate_freight_amount


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'name',
            'phone',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'pincode',
            'landmark',
        ]
        read_only_fields = ['id']


class ShipmentSerializer(serializers.ModelSerializer):
    sender_address = AddressSerializer()
    receiver_address = AddressSerializer()
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )
    shipment_items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'id',
            'awb',
            'merchant',
            'sender_address',
            'receiver_address',
            'weight_kg',
            'length_cm',
            'width_cm',
            'height_cm',
            'service_type',
            'cod_amount',
            'freight_amount',
            'is_fragile',
            'is_dangerous',
            'is_reverse',
            'original_awb',
            'status',
            'label_file',
            'items',
            'shipment_items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'awb',
            'merchant',
            'freight_amount',
            'status',
            'label_file',
            'shipment_items',
            'created_at',
            'updated_at',
        ]

    def get_shipment_items(self, obj):
        return ShipmentItemSerializer(obj.items.all(), many=True).data

    def create(self, validated_data):
        sender_data = validated_data.pop('sender_address')
        receiver_data = validated_data.pop('receiver_address')
        items_data = validated_data.pop('items', [])
        sender = Address.objects.create(**sender_data)
        receiver = Address.objects.create(**receiver_data)

        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['merchant'] = request.user

        shipment = Shipment.objects.create(
            sender_address=sender,
            receiver_address=receiver,
            freight_amount=calculate_freight_amount(
                validated_data.get('weight_kg'),
                validated_data.get('length_cm', 0),
                validated_data.get('width_cm', 0),
                validated_data.get('height_cm', 0),
                validated_data.get('service_type', Shipment.SERVICE_STANDARD),
                validated_data.get('cod_amount', 0),
            ),
            **validated_data
        )

        for item_data in items_data:
            ShipmentItem.objects.create(shipment=shipment, **item_data)

        return shipment


class ShipmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentItem
        fields = ['id', 'name', 'quantity', 'declared_value', 'hsn_code']
        read_only_fields = ['id']
