import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta

from app.models.booking import Booking, BookingStatus
from app.models.centre import DiagnosticCentre, DiagnosticTest
from app.models.payment import Payment, PaymentStatus
from app.tests.conftest import TestingSessionLocal
from sqlalchemy.future import select

@pytest.fixture
async def setup_data(db_session, test_user):
    # Create Centre and Test
    centre = DiagnosticCentre(name="Test Centre", location="Test Loc")
    db_session.add(centre)
    await db_session.commit()
    await db_session.refresh(centre)

    test = DiagnosticTest(centre_id=centre.id, name="Blood Test", price=100.0)
    db_session.add(test)
    await db_session.commit()
    await db_session.refresh(test)

    # Create Booking
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    booking = Booking(
        user_id=test_user.id,
        test_id=test.id,
        centre_id=centre.id,
        appointment_time=future_time,
        amount=100.0,
        status=BookingStatus.PENDING
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    return booking

@pytest.mark.asyncio
async def test_webhook_idempotency(client: AsyncClient, setup_data: Booking):
    # We will fire 3 concurrent requests to the webhook with the same provider_event_id
    payload = {
        "provider_event_id": "event_12345",
        "booking_id": setup_data.id,
        "status": "SUCCESS"
    }

    # Fire 3 requests concurrently
    tasks = [
        client.post("/api/v1/payments/webhook", json=payload),
        client.post("/api/v1/payments/webhook", json=payload),
        client.post("/api/v1/payments/webhook", json=payload)
    ]
    
    responses = await asyncio.gather(*tasks)

    # All responses should be 200 OK because of idempotency
    for res in responses:
        assert res.status_code == 200
        assert res.json()["provider_event_id"] == "event_12345"
        assert res.json()["status"] == "SUCCESS"

    # Now verify in the DB that only ONE payment record was created
    async with TestingSessionLocal() as session:
        query = select(Payment).filter(Payment.provider_event_id == "event_12345")
        result = await session.execute(query)
        payments = result.scalars().all()

        assert len(payments) == 1

        # Verify booking status is CONFIRMED
        query_booking = select(Booking).filter(Booking.id == setup_data.id)
        result_booking = await session.execute(query_booking)
        booking = result_booking.scalars().first()

        assert booking.status == BookingStatus.CONFIRMED
