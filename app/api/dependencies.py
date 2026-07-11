from app.core.exceptions import InvalidToken, ClientNotAuthorized
from app.core.security import oauth2_scheme_seller, oauth2_scheme_partner
from app.database.models import Seller, DeliveryPartner
from app.services.delivery_partner import DeliveryPartnerService
from app.services.shipment import ShipmentService
from app.services.seller import SellerService
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_session
from app.services.shipment_event import ShipmentEventService
from app.utils import decode_access_token
from app.database.redis import is_jti_blacklisted
from uuid import UUID



#Asynchronus database session dep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]

#Shipment service dep
def get_shipment_service(session: SessionDep):
    return ShipmentService(session=session, partner_service=DeliveryPartnerService(session=session),
                           event_service=ShipmentEventService(session=session))

ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]



#Access token data dep
async def _get_access_token(token: str) -> dict:
    data = decode_access_token(token= token)
    if data is None or await is_jti_blacklisted(data["jti"]):
        raise InvalidToken()
    return data

#Seller access token data
async def get_seller_access_token(token: Annotated[str, Depends(oauth2_scheme_seller)]) -> dict:
   return await _get_access_token(token)

#Delivery Partner access token data
async def get_partner_access_token(token: Annotated[str, Depends(oauth2_scheme_partner)]) -> dict:
   return await _get_access_token(token)


#logged In Seller
async def get_current_seller(token_data: Annotated[dict, Depends(get_seller_access_token)],
                       session:SessionDep) :
    seller =  await session.get(Seller, UUID(token_data["user"]["id"]))
    if seller is None:
        raise ClientNotAuthorized()

    return seller

#Seller dep
SellerDep = Annotated[Seller, Depends(get_current_seller)]

#logged in Delivery Partner
async def get_current_partner(token_data: Annotated[dict, Depends(get_partner_access_token)],
                       session:SessionDep):
    partner = await session.get(DeliveryPartner, UUID(token_data["user"]["id"]))
    if partner is None:
        raise ClientNotAuthorized()

    return partner

#Delivery partner dep
DeliveryPartnerDep = Annotated[DeliveryPartner, Depends(get_current_partner)]


#Seller service dependency
def get_seller_service(session: SessionDep):
    return SellerService(session=session)

SellerServiceDep = Annotated[SellerService,Depends(get_seller_service)]

# Delivery partner service dependency
def get_delivery_partner_service(session: SessionDep):
    return DeliveryPartnerService(session=session)

DeliveryPartnerServiceDep = Annotated[DeliveryPartnerService, Depends(get_delivery_partner_service)]