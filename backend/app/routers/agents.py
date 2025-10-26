from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from pydantic import BaseModel

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
        select(models.Agent).where(models.Agent.user_id == current_user.id).options(selectinload(models.Agent.model_ai))
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
                model_ai_name = agent.model_ai.name if agent.model_ai else "Neznámý model",
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
    agent_dict = agent_data.model_dump()
    agent_dict['user_id'] = current_user.id
    
    new_agent = models.Agent(**agent_dict)
    db.add(new_agent)
    await db.commit()

    result = await db.execute(
        select(models.Agent)
        .options(selectinload(models.Agent.model_ai))
        .where(models.Agent.id == new_agent.id)
    )
    created_agent = result.scalar_one()

    return schemas.AgentResponse(
        id=created_agent.id,
        name=created_agent.name,
        description=created_agent.description,
        prompt=created_agent.prompt,
        model_ai_name=created_agent.model_ai.name if created_agent.model_ai else "Neznámý model",
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
    for field, value in agent_data.dict(exclude_unset=True).items():
        setattr(agent, field, value)
    await db.commit()
    await db.refresh(agent)
    return agent



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
