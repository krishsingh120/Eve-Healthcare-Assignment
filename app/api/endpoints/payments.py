from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentSimulateRequest, PaymentWebhookPayload, PaymentResponse
from app.services import payment as payment_service

router = APIRouter()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def simulate_payment(
    request: PaymentSimulateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    force_status: Optional[str] = Query(None, description="Force status to SUCCESS or FAILED for testability")
):
    """
    Simulate a payment for a booking. 
    Updates the booking status and creates a Payment record atomically.
    """
    return await payment_service.process_simulated_payment(db, request, current_user.id, force_status)

@router.post("/webhook", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def payment_webhook(
    payload: PaymentWebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Idempotent webhook for simulated payment providers.
    Uses database unique constraint on provider_event_id to ensure idempotency.
    """
    return await payment_service.process_webhook(db, payload)
