# passwords, jwt tokens, and other security-related functions
# Tento soubor obsahuje konkrétní, nízkoúrovňové funkce pro práci s hesly a tokeny. Je to "nástrojárna" pro bezpečnost.
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from . import config

# 1. Nastavení pro hashování hesel
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Konstanty pro JWT tokeny
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token vyprší za 30 minut

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Ověří, zda se zadané heslo shoduje s hashem."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Vytvoří hash z hesla."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Vytvoří nový JWT přístupový token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt