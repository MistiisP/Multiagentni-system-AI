# passwords, jwt tokens, and other security-related functions
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from . import config

#settings for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#JWT token constants
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 80

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ Verify if the provided password matches the hashed password from database. """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """ Creates a hash from password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """ Creates a new JWT token that expires after the specified time. """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt