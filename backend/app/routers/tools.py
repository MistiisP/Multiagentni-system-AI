from fastapi import APIRouter
from ..utils.tools import TOOLS_DEFINITIONS

router = APIRouter(
    prefix="/tools",
    tags=["tools"]
)

@router.get("/", summary="Get a list of tools")
async def get_tools():
    """
        Retrieve all available tool definiions (name, description, parameters, etc.).
    """
    return TOOLS_DEFINITIONS