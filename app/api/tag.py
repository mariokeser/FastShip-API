from enum import Enum

class APITag(str, Enum):
    SHIPMENTS = "Shipment"
    SELLER = "Seller"
    PARTNER = "Delivery Partner"
