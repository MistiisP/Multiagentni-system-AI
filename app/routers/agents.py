from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from ..db.database import get_db
from ..db import models

router = APIRouter(prefix="/agents", tags=["agents"])

class AgentCreate(BaseModel):
    name: str
    prompt: Optional[str] = None
    model_ai_id: Optional[int] = None

class AgentResponse(BaseModel):
    id: int
    name: str
    prompt: Optional[str] = None


@router.get("/", response_model=List[AgentResponse])
async def get_all_agents(db: AsyncSession = Depends(get_db)):
    """Získá všechny dostupné agenty"""
    query = select(models.Agent)
    result = await db.execute(query)
    agents = result.scalars().all()
    
    return [
        AgentResponse(id=agent.id, name=agent.name, prompt=agent.prompt)
        for agent in agents
    ]


@router.post("/", response_model=AgentResponse)
async def create_agent(agent_data: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Vytvoří nového agenta"""
    # Kontrola, zda agent s tímto jménem již existuje
    query = select(models.Agent).where(models.Agent.name == agent_data.name)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Agent with this name already exists")
    
    # Vytvoření nového agenta
    new_agent = models.Agent(
        name=agent_data.name,
        prompt=agent_data.prompt,
        model_ai_id=agent_data.model_ai_id
    )
    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)
    
    return AgentResponse(
        id=new_agent.id,
        name=new_agent.name,
        prompt=new_agent.prompt
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """Získá jednoho agenta podle ID"""
    agent = await db.get(models.Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        prompt=agent.prompt
    )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: int, agent_data: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Aktualizuje agenta"""
    agent = await db.get(models.Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Aktualizace údajů
    agent.name = agent_data.name
    agent.prompt = agent_data.prompt
    agent.model_ai_id = agent_data.model_ai_id
    
    await db.commit()
    await db.refresh(agent)
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        prompt=agent.prompt
    )


@router.delete("/{agent_id}", response_model=dict)
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """Smaže agenta"""
    agent = await db.get(models.Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    await db.delete(agent)
    await db.commit()
    
    return {"message": "Agent deleted successfully"}