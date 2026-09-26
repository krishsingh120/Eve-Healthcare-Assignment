from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tests = relationship("DiagnosticTest", back_populates="centre", cascade="all, delete-orphan")


class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(Integer, ForeignKey("diagnostic_centres.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    centre = relationship("DiagnosticCentre", back_populates="tests")
