from .user import UserService
from app.database.models import DeliveryPartner, Shipment, Location, ServiceableLocation
from app.api.schemas.delivery_partner import DeliveryPartnerCreate
from typing import Sequence, cast
from sqlmodel import select
from ..core.exceptions import DeliveryPartnerNotAvailable


class DeliveryPartnerService(UserService):
    def __init__(self, session):
        super().__init__(model=DeliveryPartner, session=session)

    async def add(self, delivery_partner: DeliveryPartnerCreate ):
        partner= await self._add_user(delivery_partner.model_dump(exclude={"serviceable_zip_codes"}),
                                      "partner")
        partner = cast(DeliveryPartner, partner)

        for zip_code in delivery_partner.serviceable_zip_codes:
          location = await self.session.get(Location, zip_code)
          partner.serviceable_locations.append(
              location if location else Location(zip_code=zip_code)
          )

        return await self._update(partner)

    async def get_partner_by_zipcode(self, zipcode: int) -> Sequence[DeliveryPartner]:
        return  (
            await self.session.scalars(select(DeliveryPartner)
                                       .join(DeliveryPartner.serviceable_locations)
                                       .where(Location.zip_code == zipcode))
        ).all()



    async def assign_shipment(self, shipment: Shipment):
        eligible_partners = await self.get_partner_by_zipcode(shipment.destination)
        for partner in eligible_partners:
            if partner.current_handling_capacity > 0:
                partner.shipments.append(shipment)
                return partner
        raise DeliveryPartnerNotAvailable()

    async def update(self, partner: DeliveryPartner, zip_codes: list[int] | None ):
        if zip_codes is not None:
            partner.serviceable_locations.clear()
            for zip_code in zip_codes:
                location = await self.session.get(Location, zip_code)
                partner.serviceable_locations.append(location if location else Location(zip_code=zip_code))
        return await self._update(partner)


    async def token(self, email, password) -> str:
        return await self._generate_token(email, password)

