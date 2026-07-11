from pydantic import BaseModel, Field, EmailStr
from app.database.models import ShipmentStatus, ShipmentEvent, TagName
from datetime import datetime
from uuid import UUID





class BaseShipment(BaseModel):
    content: str = Field( max_length=100)
    weight: float = Field(description="Weight of the shipment in kilograms (kg)", le=25)
    destination: int = Field(description="location zipcode",
                             examples=[11001, 11002])




class ShipmentCreate(BaseShipment):
    """Shipment details to create a new shipment"""
    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)



class TagRead(BaseModel):
    name: TagName
    instructions: str


class ShipmentRead(BaseShipment):
    id:UUID
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime
    tags:list[TagRead]


class ShipmentUpdate(BaseModel):
    location: int|None = Field(default=None)
    description: str |None = Field(default=None)
    verification_code: str | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)







