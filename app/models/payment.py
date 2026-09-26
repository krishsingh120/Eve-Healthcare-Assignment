import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class PaymentStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    provider_event_id = Column(String, unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    booking = relationship("Booking")
