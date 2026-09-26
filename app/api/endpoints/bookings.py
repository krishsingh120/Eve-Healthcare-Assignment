from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.booking import BookingResponse, BookingCreate
from app.services import booking as booking_service

router = APIRouter()

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new diagnostic test booking for the current user.
    """
    return await booking_service.create_booking(db, booking_in, current_user.id)

@router.get("/", response_model=List[BookingResponse])
async def list_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all bookings for the current user.
    """
    return await booking_service.get_bookings(db, current_user.id, skip=skip, limit=limit)

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific booking. Returns 404 if not found or belongs to another user.
    """
    booking = await booking_service.get_booking(db, booking_id, current_user.id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking

@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a pending or confirmed booking, provided the appointment time hasn't passed.
    """
    return await booking_service.cancel_booking(db, booking_id, current_user.id)
