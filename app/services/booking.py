from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List
from datetime import datetime, timezone

from app.models.booking import Booking, BookingStatus
from app.models.centre import DiagnosticTest
from app.schemas.booking import BookingCreate

async def get_bookings(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[Booking]:
    query = select(Booking).filter(Booking.user_id == user_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_booking(db: AsyncSession, booking_id: int, user_id: int) -> Booking | None:
    query = select(Booking).filter(Booking.id == booking_id, Booking.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().first()

async def create_booking(db: AsyncSession, booking_in: BookingCreate, user_id: int) -> Booking:
    if booking_in.appointment_time.tzinfo is None:
        booking_in.appointment_time = booking_in.appointment_time.replace(tzinfo=timezone.utc)

    if booking_in.appointment_time <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Appointment time must be in the future")

    test_query = select(DiagnosticTest).filter(
        DiagnosticTest.id == booking_in.test_id,
        DiagnosticTest.centre_id == booking_in.centre_id
    )
    test_result = await db.execute(test_query)
    test = test_result.scalars().first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found or does not belong to the specified centre."
        )

    db_booking = Booking(
        user_id=user_id,
        test_id=booking_in.test_id,
        centre_id=booking_in.centre_id,
        appointment_time=booking_in.appointment_time,
        amount=test.price,
        status=BookingStatus.PENDING
    )
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)
    return db_booking

async def cancel_booking(db: AsyncSession, booking_id: int, user_id: int) -> Booking:
    booking = await get_booking(db, booking_id, user_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending or confirmed bookings can be cancelled")

    now_utc = datetime.now(timezone.utc)
    # Ensure booking appointment_time is timezone aware for comparison
    appt_time = booking.appointment_time
    if appt_time.tzinfo is None:
        appt_time = appt_time.replace(tzinfo=timezone.utc)

    if appt_time <= now_utc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel a past appointment")

    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)
    return booking
