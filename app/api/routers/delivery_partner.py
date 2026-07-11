from fastapi import APIRouter, Depends, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from ..dependencies import DeliveryPartnerDep, get_partner_access_token, DeliveryPartnerServiceDep, SessionDep
from ..schemas.delivery_partner import DeliveryPartnerRead, DeliveryPartnerCreate, DeliveryPartnerUpdate, \
    DeliveryPartnerShipments
from app.database.redis import add_jti_to_blacklist
from typing import Annotated, Literal
from ..schemas.shipment import ShipmentRead
from ...core.exceptions import NothingToUpdate
from ..tag import APITag
from app.core.security import TokenData
from pydantic import EmailStr, BaseModel
from ...database.models import Shipment
from ...utils import TEMPLATE_DIR
from fastapi.templating import Jinja2Templates
from ...config import app_settings
from fastapi.responses import HTMLResponse
from sqlalchemy import select, asc, desc
from math import ceil



router = APIRouter(prefix="/partner", tags=[APITag.PARTNER])



@router.post("/signup", response_model=DeliveryPartnerRead)
async def register_delivery_partner(
        partner: DeliveryPartnerCreate,
        service: DeliveryPartnerServiceDep
):
    return await service.add(partner)


@router.post("/token", response_model=TokenData)
async def login_delivery_partner(request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
                       service: DeliveryPartnerServiceDep):
    token = await service.token(request_form.username, request_form.password)
    return {
        "access_token" : token,
        "token_type": "bearer"}

## Get partner profile
@router.get("/me", response_model=DeliveryPartnerRead)
async def get_delivery_partner_profile(partner: DeliveryPartnerDep):
    return partner


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 10
    order: Literal["asc", "desc"] = "asc"

def get_pagination_params(page:int=1, page_size:int=10, order: Literal["asc", "desc"] = "asc") -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size, order=order)

###Get all shipments assigned to the partner
@router.get("/shipments", response_model=DeliveryPartnerShipments)
async def get_shipments(partner: DeliveryPartnerDep, session: SessionDep,
                        pagination:Annotated[PaginationParams, Depends(get_pagination_params)]):
    result = await session.scalars(
        select(Shipment)
        .where(Shipment.delivery_partner_id == partner.id)
        .limit(pagination.page_size)
        .offset((pagination.page-1) * pagination.page_size)
        .order_by(asc(Shipment.created_at) if pagination.order == "asc" else desc(Shipment.created_at))
    )
    return {
        "shipments": result.all(),
        "total_shipments": len(partner.shipments),
        "page": pagination.page,
        "total_pages": ceil(len(partner.shipments) / pagination.page_size)

    }




### Verify Delivery Partner Email
@router.get("/verify")
async def verify_delivery_partner_email(token: str, service: DeliveryPartnerServiceDep):
    await service.verify_email(token)
    return {"detail": "Account verified"}



### Update the logged in delivery partner
@router.patch("/", response_model=DeliveryPartnerRead)
async def update_delivery_partner(
        partner_update: DeliveryPartnerUpdate,
        partner: DeliveryPartnerDep,
        service: DeliveryPartnerServiceDep
):
     update = partner_update.model_dump(exclude_unset=True)
     if not update:
         raise NothingToUpdate()
     zip_codes = update.pop("serviceable_zip_codes", None)
     if update:
        partner.sqlmodel_update(update)
     return await service.update(partner, zip_codes)


### Email Password Reset Link
@router.get("/forgot_password")
async def forgot_password(email:EmailStr , service: DeliveryPartnerServiceDep):
    await service.send_password_reset_link(email, router_prefix=router.prefix)
    return {"detail": "Check email for password reset link"}


###Password Reset Form
@router.get("/reset_password_form")
async def get_reset_password_form(request: Request, token: str):
    templates = Jinja2Templates(directory=TEMPLATE_DIR)
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={"reset_url": f"http://{app_settings.APP_DOMAIN}{router.prefix}/reset_password?token={token}"}
    )

### Reset Partner Password
@router.post("/reset_password", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    token: str ,
    password: Annotated[str, Form()],
    service: DeliveryPartnerServiceDep
    ):
        is_success = await service.reset_password(token, password)
        templates = Jinja2Templates(directory=TEMPLATE_DIR)
        return templates.TemplateResponse(
                request=request,
                name="password/reset_password_success.html" if is_success else "password/reset_password_failed.html"
            )



@router.get("/logout")
async def logout_delivery_partner(token_data: Annotated[dict, Depends(get_partner_access_token)]):
    await add_jti_to_blacklist(token_data["jti"])
    return {
        "detail": "Successfully logged out."
    }