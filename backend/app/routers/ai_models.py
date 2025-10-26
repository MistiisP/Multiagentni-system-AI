from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..db import database, models, schemas
from ..services.auth import get_current_user

router = APIRouter(
    prefix="/ai_models",
    tags=["ai_models"],
)

@router.get("/", response_model=List[schemas.AIModelResponse], summary="Get a list of all AI models belonging to the current user")
async def get_all_ai_models(
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Fetches all AI models for the authenticated user.
        - **Requires authentication.**
        - Returns a list of agent objects.
    """
    result = await db.execute(
        select(models.ModelOfAI).where(models.ModelOfAI.user_id == current_user.id))
    ai_models = result.scalars().all()
    return ai_models



@router.post("/", response_model=schemas.AIModelResponse, status_code=status.HTTP_201_CREATED, summary="Creates a new AI model for the current user")
async def create_ai_model(
    model_data: schemas.AIModelCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Creates a new AI model based on provided data.
        - **model_data**: Pydantic model with AI model details.
    """
    new_model = models.ModelOfAI(
        name=model_data.name,
        user_id=current_user.id,
        model_identifier=model_data.model_identifier,
        api_key=model_data.api_key
    )
    db.add(new_model)
    await db.commit()
    await db.refresh(new_model)
    return new_model



    

@router.put("/{model_id}", response_model=schemas.AIModelResponse, summary="Update an AI model")
async def update_ai_model(
    model_id: int,
    model_data: schemas.AIModelUpdate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Updates an agent's attributes.
        - **agent_id**: The ID of the agent to update.
        - **agent_data**: A Pydantic model containing the fields to update.
    """
    ai_model = await db.get(models.ModelOfAI, model_id)
    if not ai_model:
        raise HTTPException(status_code=404, detail="AI model not found")
    for field, value in model_data.dict(exclude_unset=True).items():
        setattr(ai_model, field, value)
    await db.commit()
    await db.refresh(ai_model)
    return ai_model



@router.delete("/{model_id}", summary="Delete an AI model")
async def delete_ai_model(
    model_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    """
        Deletes an AI model by its ID.
        Removes the reference to this AI model for all associated agents.
    """
    ai_model = await db.get(models.ModelOfAI, model_id)
    if not ai_model:
        raise HTTPException(status_code=404, detail="AI model not found")

    agents = (await db.execute(
        select(models.Agent).where(models.Agent.model_ai_id == model_id)
    )).scalars().all()

    for agent in agents:
        agent.ai_model_id = None

    await db.delete(ai_model)
    await db.commit()
    return {"detail": "AI model smazan"}