from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Merchant, WebhookEndpoint

User = get_user_model()


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = [
            "id",
            "company_name",
            "gstin",
            "address",
            "api_key",
            "credit_limit",
            "active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "api_key",
            "credit_limit",
            "active",
            "created_at",
        ]

    def validate_gstin(self, value):
        if value and not is_valid_gstin(value):
            raise serializers.ValidationError("Enter a valid GSTIN.")
        return value


def is_valid_gstin(value):
    if not value:
        return True

    if len(value) != 15 or not value.isalnum() or value != value.upper():
        return False

    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    factor = 2
    total = 0

    for char in reversed(value[:-1]):
        code = alphabet.find(char)
        if code == -1:
            return False

        addend = factor * code
        addend = (addend // 36) + (addend % 36)
        total += addend
        factor = 1 if factor == 2 else 2

    check_code = (36 - (total % 36)) % 36
    return alphabet[check_code] == value[-1]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(max_length=255)
    gstin = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=15
    )
    address = serializers.JSONField(required=False)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def validate_gstin(self, value):
        if value and not is_valid_gstin(value):
            raise serializers.ValidationError(
                "Enter a valid GSTIN."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        merchant_data = {
            "company_name": validated_data.pop("company_name"),
            "gstin": validated_data.pop("gstin", ""),
            "address": validated_data.pop("address", {}),
        }

        password = validated_data.pop("password")

        # get username, fallback to email
        username = validated_data.get(
            "username"
        ) or validated_data["email"]

        validated_data["username"] = username

        # FIXED: no duplicate email
        user = User.objects.create_user(
            **validated_data
        )

        user.set_password(password)
        user.save()

        Merchant.objects.create(
            user=user,
            **merchant_data
        )

        return user


class ProfileSerializer(serializers.ModelSerializer):
    merchant = MerchantSerializer(
        source="merchant_profile",
        required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone",
            "is_merchant",
            "is_ops",
            "merchant",
        ]
        read_only_fields = [
            "id",
            "email",
            "is_merchant",
            "is_ops",
        ]

    def update(self, instance, validated_data):
        merchant_data = validated_data.pop(
            "merchant_profile",
            None
        )

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        if merchant_data and hasattr(
            instance,
            "merchant_profile"
        ):
            merchant = instance.merchant_profile

            for field, value in merchant_data.items():
                setattr(merchant, field, value)

            merchant.save()

        return instance


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = [
            "id",
            "url",
            "secret",
            "events",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "secret",
            "is_active",
            "created_at",
        ]

    def validate_events(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Events must be a list."
            )
        return value


class TrackFlowTokenObtainPairSerializer(
    TokenObtainPairSerializer
):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["profile"] = ProfileSerializer(
            self.user
        ).data
        return data