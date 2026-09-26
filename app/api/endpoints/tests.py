from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.centre import DiagnosticTestResponse, DiagnosticTestCreate
from app.services import centre as centre_service

router = APIRouter()

@router.get("/", response_model=List[DiagnosticTestResponse])
async def list_tests(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    centre_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all diagnostic tests, optionally filtering by centre_id.
    Paginated.
    """
    tests = await centre_service.get_tests(db, skip=skip, limit=limit, centre_id=centre_id)
    return tests

@router.post("/", response_model=DiagnosticTestResponse, status_code=status.HTTP_201_CREATED)
async def create_test(
    test_in: DiagnosticTestCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new diagnostic test for a centre. Admin only.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    return await centre_service.create_test(db, test_in)
