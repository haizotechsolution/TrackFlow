from .models import Carrier
from .adapters.delhivery import DelhiveryAdapter
from .adapters.xpressbees import XpressbeesAdapter
from .adapters.bluedart import BlueDartAdapter


ADAPTERS = {
    'DELHIVERY': DelhiveryAdapter,
    'XPRESSBEES': XpressbeesAdapter,
    'BLUEDART': BlueDartAdapter,
}


class CarrierService:
    @staticmethod
    def get_adapter(carrier_code):
        carrier = Carrier.objects.get(code=carrier_code)

        adapter_class = ADAPTERS.get(carrier_code)

        if not adapter_class:
            raise Exception('Unsupported carrier')

        return adapter_class(carrier)