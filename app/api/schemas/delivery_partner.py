from app.database.models import Location
from pydantic import  BaseModel, EmailStr, Field


class DeliveryPartnerCreate(BaseModel):
    name: str
    email: EmailStr
    serviceable_zip_codes: list[int]
    max_handling_capacity: int
    password: str


class DeliveryPartnerUpdate(BaseModel):
    serviceable_zip_codes: list[int] |None = Field(default=None)
    max_handling_capacity: int | None = Field(default=None)



class DeliveryPartnerRead(BaseModel):
    name: str
    email: EmailStr
    serviceable_locations: list[Location]
    max_handling_capacity: int

class Shipment(BaseModel):
    content: str

class DeliveryPartnerShipments(BaseModel):
    shipments: list[Shipment]
    total_shipments: int
    page: int
    total_pages: int
