# EVE Diagnostics

A diagnostic test booking and simulated payment platform backend service.

## Tech Stack
- Python 3.11+, FastAPI
- PostgreSQL (SQLAlchemy 2.0 + Alembic)
- Pydantic v2
- JWT Authentication
- Pytest (async testing), Docker, Structured Logging

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/krishsingh120/Eve-Healthcare-Assignment.git
   cd Eve-Healthcare-Assignment
   ```

2. **Docker Compose (Recommended):**
   This spins up both the FastAPI application and a PostgreSQL database.
   ```bash
   docker-compose up --build -d
   ```
   The API will be available at `http://localhost:8000`. You can view the auto-generated Swagger documentation at `http://localhost:8000/docs`.

3. **Local Development (Without Docker):**
   - Ensure PostgreSQL is running and update `.env` with your credentials.
   - Install dependencies: `pip install -r requirements.txt`
   - Run migrations: `alembic upgrade head`
   - Start the server: `uvicorn app.main:app --reload`

## Database & ER Diagram

**Entities & Relationships:**
- **User (1) — (N) Booking**: A user can have many bookings.
- **DiagnosticCentre (1) — (N) DiagnosticTest**: A centre offers many tests.
- **DiagnosticTest (1) — (N) Booking**: A test can be booked many times.
- **Booking (1) — (N) Payment**: A booking can have multiple payment attempts (e.g. failures followed by a success).

**Key Constraints & Indexes:**
- `users.email`: Unique index for fast lookups during login/signup.
- `payments.provider_event_id`: Unique constraint enforcing webhook idempotency at the database level.
- `bookings.user_id`: Indexed to quickly fetch a user's booking history.

## API Endpoints Summary

- `POST /api/v1/auth/signup`: Create a new user.
- `POST /api/v1/auth/login`: Authenticate and get JWT.
- `GET /api/v1/centres/`: List diagnostic centres.
- `GET /api/v1/tests/`: List tests.
- `POST /api/v1/bookings/`: Book a test (requires auth).
- `GET /api/v1/bookings/`: View your bookings (requires auth).
- `POST /api/v1/bookings/{id}/cancel`: Cancel a pending booking.
- `POST /api/v1/payments/`: Simulate a payment (resolves to SUCCESS/FAILED and triggers state change).
- `POST /api/v1/payments/webhook`: Idempotent webhook receiver for payment updates.

## Important Assumptions Made
1. **Webhook Idempotency**: Relying on database unique constraints (`IntegrityError`) for idempotency is robust against race conditions, compared to reading a record then writing.
2. **Booking Price Snapshot**: The `amount` field in the `Booking` model snapshots the `DiagnosticTest` price at the time of booking to prevent historical bookings from changing if the test price is updated later.
3. **Webhook Conflict Policy**: If a webhook tries to revert a `CONFIRMED` booking back to `FAILED` (or vice versa), the app logs a warning rather than blindly overwriting the state, preventing state corruption.

## What I'd improve with more time
1. **Redis Caching**: Cache the `/centres` and `/tests` lists to reduce DB read load.
2. **Celery**: Offload payment simulation processing and email notifications to background tasks.
3. **Rate Limiting**: Implement strict rate limiting for `/auth/login` and `/payments/webhook` to prevent abuse.
