from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services import auth as auth_service

router = APIRouter()

@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new user.
    """
    user = await auth_service.create_user(db, user_in)
    return user

@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    OAuth2 compatible token login, getting an access token for future requests.
    Using standard JSON body for ease of Pydantic validation (as requested).
    """
    access_token = await auth_service.authenticate_user(db, user_in)
    return {"access_token": access_token, "token_type": "bearer"}
