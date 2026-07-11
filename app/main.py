from fastapi import FastAPI, Request, Response
from scalar_fastapi import get_scalar_api_reference
from app.api.router import master_router
from app.core.exceptions import add_exception_handlers
from time import perf_counter
from .worker.tasks import add_log
from fastapi.middleware.cors import CORSMiddleware
from .api.tag import APITag
from app.core.logging import logger


description = """
Delivery Management System for sellers and delivery agents
### Seller
- Submit tracking links effortlessly
- Share tracking links with customers

### Delivery Agent
- Auto accept shipments
- Track and update shipment status
- Email and SMS notifications
"""


app = FastAPI(
    title="FastShip",
    description=description,
    docs_url=None,
    redoc_url=None,
    version="0.1.0",
    openapi_tags=[
        {"name": APITag.SHIPMENTS,
         "description": "- Operations related to shipments"},
        { "name": APITag.SELLER,
         "description": "- Operations related to seller"},
        {"name": APITag.PARTNER,
         "description" : "- Operations related to delivery partner"}])




app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)




app.include_router(master_router)

add_exception_handlers(app)


# Add custom middleware
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    start = perf_counter()

    try:
        response: Response = await call_next(request)
    except Exception as exc:
        end = perf_counter()
        time_taken = round(end - start, 2)
        logger.critical(
            "%s %s - UNHANDLED EXCEPTION: %s (%.2f s)",
            request.method, request.url.path, exc, time_taken,
            exc_info=True

        )
        raise

    end = perf_counter()
    time_taken = round(end - start, 2)

    log_message = "%s %s (%d) %.2f s" % (
        request.method, request.url.path, response.status_code, time_taken
    )

    if response.status_code >= 500:
        logger.error(log_message)
    elif response.status_code >= 400:
        logger.warning(log_message)
    else:
        logger.info(log_message)

    add_log.delay(f"{request.method} {request.url} ({response.status_code}) {time_taken} s")

    return response





@app.get("/")
def read_root():
    return  {"detail": "server is running..."}


@app.get("/docs", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )