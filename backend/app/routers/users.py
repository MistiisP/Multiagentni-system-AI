from fastapi import APIRouter, Depends, HTTPException
from ..db.models import User
from ..db import schemas
from ..services.auth import get_current_user

router = APIRouter(
    prefix="/users", 
    tags=["users"]
)

@router.get("/me", response_model=schemas.User, summary="Get current user info")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """ 
         Retrieve information about the currently authenticated user.
        - **Authentication required.**
        - Returns user details such as ID, name, and email.   
    """
    return current_user