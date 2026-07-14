# FastShip API

Backend application for a delivery management system. The application connects sellers, delivery partners, and shipments, enabling shipment creation, status tracking, delivery partner assignment, user authentication, email/WhatsApp notifications, and leaving a review after delivery.

## What the backend provides

- Seller registration and login.
- Delivery partner registration and login.
- JWT authentication for protected routes.
- Creation, viewing, updating, and cancellation of shipments.
- Automatic linking of a shipment with a delivery partner.
- Shipment tracking via a public tracking page.
- Shipment status timeline: `placed`, `in_transit`, `out_for_delivery`, `delivered`, `cancelled`.
- Shipment tagging, e.g. `express`, `standard`, `fragile`, `heavy`, `international`.
- Sending email notifications and HTML email templates.
- Sending WhatsApp messages via the Twilio service.
- Password reset and email verification.
- Shipment review after delivery.
- Request logging and log storage via a Celery task.
- API documentation via the Scalar UI interface.

## Technologies used

- **Python 3.13** - the backend application's programming language.
- **FastAPI** - web framework for building the REST API.
- **Pydantic** and **Pydantic Settings** - data validation and reading configuration from the `.env` file.
- **SQLModel** and **SQLAlchemy** - ORM layer and database models.
- **PostgreSQL** - main relational database.
- **AsyncPG** - async PostgreSQL driver.
- **Alembic** - database migrations.
- **Redis** - temporary data storage and broker for background tasks.
- **Celery** - background tasks for email, WhatsApp, and logging.
- **FastAPI Mail** - sending email messages and HTML templates.
- **Jinja2** - HTML templates for emails, tracking, review, and password reset.
- **Twilio** - sending WhatsApp notifications.
- **JWT / PyJWT** - access tokens for authentication.
- **Passlib** and **bcrypt** - password hashing.
- **Docker** and **Docker Compose** - running the application, PostgreSQL database, Redis service, and Celery worker.
- **Pytest** and **pytest-asyncio** - application testing.
- **Scalar FastAPI** - API documentation display.

## Project structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── routers/        # API routes for shipments, sellers, and partners
│   │   ├── schemas/        # Pydantic/SQLModel schemas for request and response data
│   │   ├── dependencies.py # Dependency injection for services, session, and auth
│   │   └── router.py       # Main API router
│   ├── core/               # Security, logging, and exception handlers
│   ├── database/           # Database session, Redis, and SQLModel models
│   ├── services/           # Application business logic
│   ├── templates/          # HTML templates
│   ├── tests/              # Pytest tests
│   ├── worker/             # Celery tasks
│   ├── config.py           # Application configuration from environment variables
│   └── main.py             # FastAPI application
├── migrations/             # Alembic migrations
├── compose.yaml            # Docker Compose configuration
├── Dockerfile              # Docker image for the backend
├── requirements.txt        # Python dependencies
├── alembic.ini             # Alembic configuration
└── pytest.ini              # Pytest configuration
```

## Main data models

- **Seller** - the seller who creates shipments.
- **DeliveryPartner** - the delivery partner who picks up and updates shipments.
- **Shipment** - a shipment with data about contents, weight, destination, customer, and delivery partner.
- **ShipmentEvent** - a single event in the shipment timeline.
- **Tag** - labels for categorizing shipments.
- **Review** - rating and comment for a shipment.
- **Location** - a postal code that a delivery partner can cover.

## API sections

### Seller

Routes with the `/seller` prefix are used for:

- seller registration,
- login and obtaining an access token,
- fetching the profile,
- fetching all of the seller's shipments,
- email verification,
- password reset,
- logout and token blacklisting.

### Delivery Partner

Routes with the `/partner` prefix are used for:

- delivery partner registration,
- login and obtaining an access token,
- fetching the profile,
- fetching assigned shipments with pagination,
- updating partner data,
- email verification,
- password reset,
- logout and token blacklisting.

### Shipment

Routes with the `/shipment` prefix are used for:

- creating a shipment,
- fetching a single shipment,
- updating shipment status,
- cancelling a shipment,
- adding and removing tags,
- fetching shipments by tag,
- public shipment tracking,
- displaying and submitting a review.

## Configuration

The application uses a `.env` file for configuration. An example can be found in `.env.example`.

Most important environment variables:

```env
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_SERVER=
POSTGRES_PORT=
POSTGRES_DB=
REDIS_HOST=
REDIS_PORT=
JWT_SECRET=
JWT_ALGORITHM=
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_FROM_NAME=
MAIL_PORT=
MAIL_SERVER=
TWILIO_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP=
LOGTAIL_SOURCE_TOKEN=
LOGTAIL_HOST=
```

## Running via Docker Compose

```bash
docker compose up --build
```

Docker Compose runs:

- `api` - FastAPI backend on port `8000`,
- `db` - PostgreSQL database on port `5433`,
- `redis` - Redis service,
- `celery` - Celery worker for background tasks.

Once started:

- the API is available at `http://localhost:8000`
- the documentation is available at `http://localhost:8000/docs`

## Running locally without Docker

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
fastapi run app/main.py --port 8000
```

To run locally without Docker, PostgreSQL and Redis services must be running manually and the `.env` file must be filled in correctly.

## Database migrations

Alembic is used for versioning the database structure.

```bash
alembic upgrade head
```

To create a new migration:

```bash
alembic revision --autogenerate -m "description of change"
```

## Testing

Tests are located in `app/tests`.

```bash
pytest
```

The project uses `pytest-asyncio`, so tests can work with async FastAPI and database code.

## API documentation

The standard FastAPI Swagger and ReDoc are disabled, and Scalar documentation is used instead.

```text
GET /docs
```

The Scalar UI displays the OpenAPI documentation and allows browsing all routes, request bodies, response models, and authentication.

## Summary for presentation

The FastShip backend is a REST API built with the FastAPI framework. It uses a PostgreSQL database, SQLModel ORM, Alembic migrations, JWT authentication, Redis and Celery for background tasks, and email and WhatsApp integrations for notifications. The application covers the entire delivery process: from user registration, shipment creation, and delivery partner assignment to status tracking, sending notifications, and post-delivery reviews.
