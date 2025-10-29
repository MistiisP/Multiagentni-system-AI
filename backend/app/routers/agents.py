from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import delete

from ..db import database, models, schemas
from ..services.auth import get_current_user

router = APIRouter(
    prefix="/agents", 
    tags=["agents"]
)

@router.get("/", response_model = List[schemas.AgentResponse], summary="Get all agents belonging to the current user.")
async def get_all_agents(
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Fetches all agents for the authenticated user, including each agent´s associated AI model.
        - **Requires authentication.**
        - Returns a list of agent objects.
    """
    
    result = await db.execute(
        select(models.Agent).where(models.Agent.user_id == current_user.id).options(selectinload(models.Agent.models_ai))
    )
    
    agents = result.unique().scalars().all()
    
    response_agents = []
    for agent in agents:
        response_agents.append(
            schemas.AgentResponse(
                id = agent.id,
                name = agent.name,
                description = agent.description,
                prompt = agent.prompt,
                models_ai=[
                    schemas.ModelOfAIResponse(
                        id=m.id,
                        name=m.name,
                        model_identifier=m.model_identifier
                    ) for m in agent.models_ai
                ] if agent.models_ai else [],
                code = agent.code,
                tools = agent.tools
            )
        )
    
    return response_agents
    

@router.post("/", response_model=schemas.AgentResponse, status_code=status.HTTP_201_CREATED, summary="Create a new agent", description="Creates a new agent for the current user." )
async def create_agent(
    agent_data: schemas.AgentCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Creates a new agent based on the provided data.
        - **agent_data**: Pydantic model with agent details.
        - The new agent is associated with the logged-in user.
    """
    agent_dict = agent_data.model_dump(exclude={"model_ids"})
    agent_dict['user_id'] = current_user.id
    
    new_agent = models.Agent(**agent_dict)
    db.add(new_agent)
    await db.flush()

    if agent_data.model_ids:
        for model_id in agent_data.model_ids:
            model = await db.get(models.ModelOfAI, model_id)
            if not model:
                raise HTTPException(status_code=400, detail=f"Model s ID {model_id} neexistuje")
            db.add(models.AgentModelLink(agent_id=new_agent.id, model_id=model_id))
    
    await db.commit()
    
    result = await db.execute(
        select(models.Agent)
        .options(selectinload(models.Agent.models_ai))
        .where(models.Agent.id == new_agent.id)
    )
    created_agent = result.scalar_one()

    return schemas.AgentResponse(
        id=created_agent.id,
        name=created_agent.name,
        description=created_agent.description,
        prompt=created_agent.prompt,
        models_ai=[
            schemas.ModelOfAIResponse(
                id=m.id,
                name=m.name,
                model_identifier=m.model_identifier
            ) for m in created_agent.models_ai
        ] if created_agent.models_ai else [],
        tools=created_agent.tools,
        code=created_agent.code
    )
    
    

    

@router.put("/{agent_id}", summary="Update an agent",)
async def update_agent(
    agent_id: int, agent_data: schemas.AgentUpdate, 
    db: AsyncSession = Depends(database.get_db)
):
    """
        Updates an agent's attributes.
        - **agent_id**: The ID of the agent to update.
        - **agent_data**: A Pydantic model containing the fields to update.
    """
    agent = await db.get(models.Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_dict = agent_data.model_dump(exclude_unset=True, exclude={"model_ids"})

    for field, value in update_dict.items():
        setattr(agent, field, value)

    if agent_data.model_ids is not None:
        await db.execute(
            delete(models.AgentModelLink).where(models.AgentModelLink.agent_id == agent_id)
        )
        for model_id in agent_data.model_ids:
            model = await db.get(models.ModelOfAI, model_id)
            if not model:
                raise HTTPException(status_code=400, detail=f"Model s ID {model_id} neexistuje")
            db.add(models.AgentModelLink(agent_id=agent_id, model_id=model_id))

    await db.commit()
    await db.refresh(agent)

    result = await db.execute(
        select(models.Agent)
        .options(selectinload(models.Agent.models_ai))
        .where(models.Agent.id == agent_id)
    )
    updated_agent = result.scalar_one()

    return schemas.AgentResponse(
        id=updated_agent.id,
        name=updated_agent.name,
        description=updated_agent.description,
        prompt=updated_agent.prompt,
        models_ai=[
            schemas.ModelOfAIResponse(
                id=m.id,
                name=m.name,
                model_identifier=m.model_identifier
            ) for m in updated_agent.models_ai
        ] if updated_agent.models_ai else [],
        tools=updated_agent.tools,
        code=updated_agent.code
    )



@router.delete("/{agent_id}", summary="Delete an agent", description="Delete an agent and all its asociated nodes and graphs.")
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    """
        Deletes an agent by its ID.
        This operation is cascading:
            1. Finds all nodes associated with the agent.
            2. Finds and deletes all graphs that use these nodes.
            3. Deletes the nodes.
            4. Deletes the agent itself.
        - **agent_id**: The ID of the agent to delete.
    """
    agent = await db.get(models.Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await db.execute(
        delete(models.AgentModelLink).where(models.AgentModelLink.agent_id == agent_id)
    )
    
    nodes = (await db.execute(select(models.Node).where(models.Node.agent_id == agent_id))).scalars().all()
    node_ids = [node.id for node in nodes]

    if node_ids:
        graphs = (await db.execute(
            select(models.Graph).where(models.Graph.entry_node_id.in_(node_ids))
        )).scalars().all()
        for graph in graphs:
            await db.delete(graph) 
        for node in nodes:
            await db.delete(node)

    await db.delete(agent)
    await db.commit()
    return {"detail": "Agent smazan"}
