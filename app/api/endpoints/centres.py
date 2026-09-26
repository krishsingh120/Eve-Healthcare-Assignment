from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.centre import DiagnosticCentreResponse, DiagnosticCentreDetailResponse, DiagnosticCentreCreate
from app.services import centre as centre_service

router = APIRouter()

@router.get("/", response_model=List[DiagnosticCentreResponse])
async def list_centres(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    location: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all diagnostic centres, optionally filtering by location.
    Paginated.
    """
    centres = await centre_service.get_centres(db, skip=skip, limit=limit, location=location)
    return centres

@router.get("/{centre_id}", response_model=DiagnosticCentreDetailResponse)
async def get_centre(
    centre_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific diagnostic centre by ID, including its tests.
    """
    centre = await centre_service.get_centre(db, centre_id)
    if not centre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Centre not found")
    return centre

@router.post("/", response_model=DiagnosticCentreResponse, status_code=status.HTTP_201_CREATED)
async def create_centre(
    centre_in: DiagnosticCentreCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new diagnostic centre. Admin only.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    return await centre_service.create_centre(db, centre_in)
