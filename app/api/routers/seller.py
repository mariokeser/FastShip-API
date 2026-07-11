from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from ..dependencies import SellerServiceDep, get_seller_access_token, SellerDep
from ..schemas.seller import SellerCreate, SellerRead
from app.database.redis import add_jti_to_blacklist
from typing import Annotated
from pydantic import EmailStr

from ..schemas.shipment import ShipmentRead
from ...config import app_settings
from ...utils import TEMPLATE_DIR
from ..tag import APITag
from app.core.security import TokenData



router = APIRouter(prefix="/seller", tags=[APITag.SELLER])

@router.post("/signup", response_model=SellerRead)
async def register_seller(
        seller: SellerCreate,
        service: SellerServiceDep
):
    return await service.add(seller)


@router.post("/token", response_model=TokenData)
async def login_seller(request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
                       service: SellerServiceDep):
    token = await service.token(request_form.username, request_form.password)
    return {
        "access_token" : token,
        "token_type": "bearer"}


## Get seller profile
@router.get("/me", response_model=SellerRead)
async def get_seller_profile(seller: SellerDep):
    return seller

###Get all shipments created by the seller
@router.get("/shipments", response_model=list[ShipmentRead])
async def get_shipments(seller: SellerDep):
    return seller.shipments


### Verify Seller Email
@router.get("/verify")
async def verify_seller_email(token: str, service: SellerServiceDep):
    await service.verify_email(token)
    return {"detail": "Account verified"}



### Email Password Reset Link
@router.get("/forgot_password")
async def forgot_password(email:EmailStr , service: SellerServiceDep):
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

### Reset Seller Password
@router.post("/reset_password", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    token: str ,
    password: Annotated[str, Form()],
    service: SellerServiceDep
    ):
        is_success = await service.reset_password(token, password)
        templates = Jinja2Templates(directory=TEMPLATE_DIR)
        return templates.TemplateResponse(
                request=request,
                name="password/reset_password_success.html" if is_success else "password/reset_password_failed.html"
            )


@router.get("/logout")
async def logout_seller(token_data: Annotated[dict, Depends(get_seller_access_token)]):
    await add_jti_to_blacklist(token_data["jti"])
    return {
        "detail": "Successfully logged out."
    }




