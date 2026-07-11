from fastapi import APIRouter, Request, Form, status
from typing import Annotated
from ..schemas.shipment import ShipmentRead, ShipmentCreate, ShipmentUpdate
from app.database.models import Shipment, TagName
from ..dependencies import ShipmentServiceDep, SellerDep, DeliveryPartnerDep, SessionDep
from uuid import UUID
from fastapi.templating import Jinja2Templates
from ...core.exceptions import NothingToUpdate
from ...utils import TEMPLATE_DIR
from app.config import app_settings
from ..tag import APITag



router = APIRouter(prefix="/shipment", tags=[APITag.SHIPMENTS])

templates=Jinja2Templates(directory=TEMPLATE_DIR)


### Tracking details of shipment
@router.get("/track", include_in_schema=False)
async def get_tracking(request: Request, id:UUID, service: ShipmentServiceDep):
    shipment = await service.get(id)
    context= shipment.model_dump()
    context["status"] = shipment.status
    context["partner"] = shipment.delivery_partner.name
    context["timeline"] = shipment.timeline
    context["timeline"].reverse()
    return templates.TemplateResponse(
        request=request,
        name="track.html",
        context=context
    )



@router.get("/", response_model=ShipmentRead)
async def get_shipment(id:UUID, _ : SellerDep, service: ShipmentServiceDep ):

   return  await service.get(id)




@router.post("/", response_model=ShipmentRead,
             name="Create Shipment",
             description="Submit a new **shipment**",
             status_code=status.HTTP_201_CREATED,
             responses={
                 status.HTTP_201_CREATED : {"description": "Shipment created"},
                 status.HTTP_406_NOT_ACCEPTABLE: {"description": "Delivery partner not available"}
             })
async def submit_shipment(seller: SellerDep,
        shipment: ShipmentCreate,
        service: ShipmentServiceDep
) -> Shipment:

    return await service.add(shipment, seller)



@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
    partner: DeliveryPartnerDep,
    service:ShipmentServiceDep,
):
    update = shipment_update.model_dump(exclude_unset=True)
    if not update:
        raise NothingToUpdate()

    return await service.update(id=id, shipment_update=shipment_update, partner=partner)

###Get all shipments with a  tag
@router.get("/tagged", response_model=list[ShipmentRead])
async def get_shipments_with_tag(tag_name: TagName, session: SessionDep):
   tag =  await tag_name.tag(session=session)
   return tag.shipments


### Add a tag to a shipment
@router.patch("/tag", response_model=ShipmentRead)
async def add_tag_to_a_shipment(
        id: UUID,
        tag_name: TagName,
        service: ShipmentServiceDep
):
    return await service.add_tag(id, tag_name)


### Remove a tag from a shipment
@router.delete("/tag", response_model=ShipmentRead)
async def remove_tag_from_shipment(
        id: UUID,
        tag_name: TagName,
        service: ShipmentServiceDep
):
    return await service.remove_tag(id, tag_name)


#Cancel shipment by id
@router.patch("/cancel", response_model=ShipmentRead)
async def cancel_shipment(id: UUID,seller: SellerDep, service: ShipmentServiceDep):
   return await service.cancel(id, seller)

### Get a review for a shipment
@router.get("/review")
async def submit_review(request:Request, token: str):
    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={"review_url": f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}"}

    )

### Submit a review for a shipment
@router.post("/review")
async def submit_review(
        request: Request,
        token: str,
        service: ShipmentServiceDep,
        rating: Annotated[int, Form(ge=1, le=5)],
        comment: Annotated[str, Form()] | None = None

):
    is_success = await service.rate(token, rating, comment)
    return templates.TemplateResponse(
        request=request,
        name="review/review_submitted.html" if is_success else "review/review_failed.html"
    )


