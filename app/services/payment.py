import logging
import random
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentSimulateRequest, PaymentWebhookPayload

logger = logging.getLogger(__name__)

async def process_simulated_payment(db: AsyncSession, request: PaymentSimulateRequest, user_id: int, force_status: str = None) -> Payment:
    # 1. Fetch booking (with FOR UPDATE to lock the row during transaction)
    query = select(Booking).filter(Booking.id == request.booking_id, Booking.user_id == user_id).with_for_update()
    result = await db.execute(query)
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot process payment for booking in {booking.status.value} state"
        )

    # 2. Simulate processing
    if force_status in ["SUCCESS", "FAILED"]:
        payment_status = PaymentStatus.SUCCESS if force_status == "SUCCESS" else PaymentStatus.FAILED
    else:
        payment_status = random.choice([PaymentStatus.SUCCESS, PaymentStatus.FAILED])

    provider_event_id = f"evt_{uuid.uuid4().hex}"

    # 3. Create payment and update booking in the same transaction
    payment = Payment(
        booking_id=booking.id,
        provider_event_id=provider_event_id,
        amount=booking.amount,
        status=payment_status
    )
    db.add(payment)

    if payment_status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED
    
    await db.commit()
    await db.refresh(payment)
    return payment

async def process_webhook(db: AsyncSession, payload: PaymentWebhookPayload) -> Payment:
    try:
        # Start a transaction manually to ensure atomicity
        async with db.begin_nested():
            # Lock the booking to prevent race conditions from concurrent webhooks
            query = select(Booking).filter(Booking.id == payload.booking_id).with_for_update()
            result = await db.execute(query)
            booking = result.scalars().first()

            if not booking:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

            # Create payment record (this will throw IntegrityError if event_id already exists)
            payment = Payment(
                booking_id=booking.id,
                provider_event_id=payload.provider_event_id,
                amount=booking.amount,
                status=payload.status
            )
            db.add(payment)
            
            # Update booking status based on webhook
            if booking.status == BookingStatus.PENDING:
                if payload.status == PaymentStatus.SUCCESS:
                    booking.status = BookingStatus.CONFIRMED
                elif payload.status == PaymentStatus.FAILED:
                    booking.status = BookingStatus.FAILED
            else:
                # Log warning if booking state conflicts with webhook, but do NOT overwrite
                logger.warning(
                    f"Webhook conflict: Booking {booking.id} is {booking.status}, "
                    f"but webhook reports {payload.status}. Keeping current booking state."
                )

        await db.commit()
        await db.refresh(payment)
        return payment

    except IntegrityError:
        # Rollback the transaction in case of IntegrityError
        await db.rollback()
        
        # Idempotency: The unique constraint on provider_event_id was violated.
        # This means we already processed this exact event.
        # Fetch the existing payment and return it as 200 OK.
        query = select(Payment).filter(Payment.provider_event_id == payload.provider_event_id)
        result = await db.execute(query)
        existing_payment = result.scalars().first()
        
        if existing_payment:
            return existing_payment
        else:
            raise HTTPException(status_code=500, detail="Database integrity error not related to idempotency")
