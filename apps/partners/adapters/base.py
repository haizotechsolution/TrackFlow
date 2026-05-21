class BaseCarrierAdapter:
    def create_shipment(self, shipment):
        raise NotImplementedError

    def track_shipment(self, awb):
        raise NotImplementedError

    def cancel_shipment(self, awb):
        raise NotImplementedError