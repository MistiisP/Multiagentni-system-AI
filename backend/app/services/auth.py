from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..db.database import get_db
from ..db.models import User

SECRET_KEY = "secret-key-xd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 80

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
        Create a JWT access token.
        - **data**: Dictionary with user data to encode in the token (e.g., {"sub": user.email}).
        - Returns a JWT token as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
        Authenticate a user by username/email and password.
        - **db**: Async SQLAlchemy session.
        - **username**: User's email or username.
        - **password**: Plain text password to verify.
        - Returns the user object if authentication is successful, otherwise returns False.
    """
    query = select(User).where(
        (User.email == username) | (User.name == username)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        return False
    
    if not user.verify_password(password):
        return False
        
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
        Retrieve the currently authenticated user from the JWT token.
        - **token**: JWT access token from the request (in Authorization header).
        - Decodes the token, verifies its validity, and fetches the user from the database.
        - Returns the user object if authentication is successful.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    query = select(User).where(User.email == username)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    return user