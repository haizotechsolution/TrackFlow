from .models import *


def calculate_freight(
    shipment,
    merchant
):

    card = RateCard.objects.filter(
        merchant=merchant,
        active=True
    ).first()

    if not card:
        return 0

    weight_cost = (
        shipment.weight_kg *
        card.per_kg_price
    )

    total = card.base_price + weight_cost

    return total