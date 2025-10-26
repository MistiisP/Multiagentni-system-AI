from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from ..db import models, database, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional

from ..services.auth import get_current_user

router = APIRouter(
    prefix="/analytics", 
    tags=["analytics"]
)

@router.get("/agent-usage/{graph_id}", summary="Get an information about agent usages")
async def get_agent_usage_stats(
    graph_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Get agent usage statistics for a specific graph.
        - **graph_id**: ID of the graph.
        - **Authentication required.**
        - Returns:
            - Total number of executions for the graph.
            - Frequency of calls for each agent.
            - Average execution time (ms) for each agent.
            - The most used agent.
    """
    user_chats_result = await db.execute(
        select(models.Chat.id).where(models.Chat.user_id == current_user.id)
    )
    user_chat_ids = [row[0] for row in user_chats_result.fetchall()]

    result = await db.execute(
        select(models.GraphExecutionLog)
        .where(models.GraphExecutionLog.graph_id == graph_id)
        .where(models.GraphExecutionLog.chat_id.in_(user_chat_ids))
    )
    logs = result.scalars().all()
    if not logs:
        return {
            "total_executions": 0,
            "agent_call_frequency": {},
            "average_execution_times_ms": {},
            "most_used_agent": None
        }
        
    agent_calls = {}
    avg_durations = {}
    
    for log in logs:
        for agent_name in log.execution_path:
            agent_calls[agent_name] = agent_calls.get(agent_name, 0) + 1
        
        for agent_name, output in log.node_outputs.items():
            if agent_name not in avg_durations:
                avg_durations[agent_name] = []
            avg_durations[agent_name].append(output.get("duration_ms", 0))
    
    for agent in avg_durations:
        durations = [d for d in avg_durations[agent] if isinstance(d, (int, float))]
        avg_durations[agent] = sum(durations) / len(durations) if durations else 0
    
    return {
        "total_executions": len(logs),
        "agent_call_frequency": agent_calls,
        "average_execution_times_ms": avg_durations,
        "most_used_agent": max(agent_calls, key=agent_calls.get) if agent_calls else None
    }



@router.get("/execution-history/{graph_id}", summary="Get a execution history for a graph")
async def get_execution_history(
    graph_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    """
        Get execution history for a specific graph.
        - **graph_id**: ID of the graph.
        - Returns a list of execution log entries, ordered by timestamp.
    """
    result = await db.execute(
        select(models.GraphExecutionLog)
        .where(models.GraphExecutionLog.graph_id == graph_id)
        .order_by(models.GraphExecutionLog.execution_timestamp.desc())
    )
    
    return result.scalars().all()

