from decimal import Decimal


def calculate_freight(weight, rate):
    return Decimal(weight) * Decimal(rate)


def calculate_gst(amount):
    return Decimal(amount) * Decimal("0.18")