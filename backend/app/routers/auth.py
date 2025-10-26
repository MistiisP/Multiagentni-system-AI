from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from pydantic import BaseModel

from ..db.database import get_db
from ..db.models import User
from ..services.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..db import schemas

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/token", response_model=Token, summary="User login and token generation", description="Authenticates a user and returns a JWT access token for API authorization.")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
        Authenticate user and return a JWT access token.
        - **form_data**: User credentials (username and password).
        - Returns a JWT token if authentication is successful.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Špatné heslo nebo uživatelské jméno",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=80)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED, summary="Register a new user")
async def register_user(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
        Register a new user.
        - **user_data**: User registration details (email, name, password).
        - Checks for existing email and username.
        - Raises 400 if the email or username already exists.
    """
    query = select(User).where(User.email == user_data.email)
    existing_user = await db.execute(query)
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uživatel s tímto emailem již existuje",
        )
    
    query = select(User).where(User.name == user_data.name)
    existing_user = await db.execute(query)
    if existing_user.scalars().unique():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uživatel s tímto jménem už existuje",
        )

    hashed_password = User.get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user