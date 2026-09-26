from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.centre import DiagnosticCentre, DiagnosticTest
from app.schemas.centre import DiagnosticCentreCreate, DiagnosticTestCreate

async def get_centres(
    db: AsyncSession, skip: int = 0, limit: int = 100, location: Optional[str] = None
) -> List[DiagnosticCentre]:
    query = select(DiagnosticCentre).offset(skip).limit(limit)
    if location:
        query = query.filter(DiagnosticCentre.location.ilike(f"%{location}%"))
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_centre(db: AsyncSession, centre_id: int) -> DiagnosticCentre | None:
    query = select(DiagnosticCentre).options(selectinload(DiagnosticCentre.tests)).filter(DiagnosticCentre.id == centre_id)
    result = await db.execute(query)
    return result.scalars().first()

async def get_tests(
    db: AsyncSession, skip: int = 0, limit: int = 100, centre_id: Optional[int] = None
) -> List[DiagnosticTest]:
    query = select(DiagnosticTest).offset(skip).limit(limit)
    if centre_id:
        query = query.filter(DiagnosticTest.centre_id == centre_id)
    
    result = await db.execute(query)
    return result.scalars().all()

async def create_centre(db: AsyncSession, centre_in: DiagnosticCentreCreate) -> DiagnosticCentre:
    db_centre = DiagnosticCentre(**centre_in.model_dump())
    db.add(db_centre)
    await db.commit()
    await db.refresh(db_centre)
    return db_centre

async def create_test(db: AsyncSession, test_in: DiagnosticTestCreate) -> DiagnosticTest:
    # Ensure centre exists first
    centre = await db.execute(select(DiagnosticCentre).filter(DiagnosticCentre.id == test_in.centre_id))
    if not centre.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Centre not found")
        
    db_test = DiagnosticTest(**test_in.model_dump())
    db.add(db_test)
    await db.commit()
    await db.refresh(db_test)
    return db_test
