from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# Test Schemas
class DiagnosticTestBase(BaseModel):
    name: str
    price: float

class DiagnosticTestCreate(DiagnosticTestBase):
    centre_id: int

class DiagnosticTestResponse(DiagnosticTestBase):
    id: int
    centre_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Centre Schemas
class DiagnosticCentreBase(BaseModel):
    name: str
    location: str

class DiagnosticCentreCreate(DiagnosticCentreBase):
    pass

class DiagnosticCentreResponse(DiagnosticCentreBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DiagnosticCentreDetailResponse(DiagnosticCentreResponse):
    tests: List[DiagnosticTestResponse] = []
