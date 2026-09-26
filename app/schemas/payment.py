from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.payment import PaymentStatus

class PaymentSimulateRequest(BaseModel):
    booking_id: int

class PaymentWebhookPayload(BaseModel):
    provider_event_id: str
    booking_id: int
    status: PaymentStatus

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    provider_event_id: str
    amount: float
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
