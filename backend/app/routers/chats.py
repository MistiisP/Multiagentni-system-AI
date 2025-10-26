from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from ..db import database, models, schemas
from ..services.auth import get_current_user
from ..services.summarizer import get_name_summary

router = APIRouter(
    prefix="/chats", 
    tags=["chats"]
)

@router.get("/", response_model=List[schemas.ChatPreview], summary="Get all chats for the current user")
async def get_user_chats(
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Fetches all chats for the authenticated user, including each agent´s associated AI model.
        - **Requires authentication.**
        - Returns a list of chats objects.
    """
    
    result = await db.execute(
        select(models.Chat)
        .where(models.Chat.user_id == current_user.id)
        .options(selectinload(models.Chat.messages))
        .order_by(models.Chat.created_at.desc())
    )
    user_chats = result.scalars().all()

    previews = []
    for chat in user_chats:
        if not chat.messages:
            previews.append(
                schemas.ChatPreview(
                    id=chat.id,
                    name=chat.name,
                    last_message="Zatím žádné zprávy.",
                    timestamp=chat.created_at.strftime("%Y-%m-%d %H:%M"),
                    graph_id=chat.graph_id
                )
            )
            continue

        sorted_messages = sorted(chat.messages, key=lambda m: m.timestamp)
        last_message = sorted_messages[-1]

        previews.append(
            schemas.ChatPreview(
                id=chat.id,
                name=chat.name, 
                last_message=last_message.content[:50], 
                timestamp=last_message.timestamp.strftime("%Y-%m-%d %H:%M"),
                graph_id=chat.graph_id
            )
        )
    
    return previews


@router.get("/{chat_id}/messages", response_model=List[schemas.Message], summary="Get messages for a chat")
async def get_chat_messages(
    chat_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Retrieve all messages for a given chat.
        - **chat_id**: ID of the chat.
        - **Authentication required.**
        - Returns a list of messages ordered by timestamp.
    """
    result = await db.execute(
        select(models.Chat).where(
            models.Chat.id == chat_id,
            models.Chat.user_id == current_user.id
        )
    )
    chat = result.scalars().first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat nenalezen nebo nepatří uživateli"
        )

    messages = await db.execute(
        select(models.Message).where(models.Message.chat_id == chat_id)
        .order_by(models.Message.timestamp.asc())
    )
    
    return messages.scalars().all()




@router.post("/", response_model=schemas.ChatResponse, status_code=status.HTTP_201_CREATED, summary="Create a new chat")
async def create_new_chat(
    first_message_data: schemas.MessageCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Create a new chat and add the first message.
        - **first_message_data**: Content of the first message.
        - The chat name is generated automatically by function get_name_summary.
        - Returns the created chat object.
    """
    chat_name = get_name_summary(first_message_data.content) #generate name from first message

    new_chat = models.Chat(
        user_id=current_user.id,
        name=chat_name
    )
    db.add(new_chat)
    await db.flush()

    first_message = models.Message(
        content=first_message_data.content,
        chat_id=new_chat.id,
        sender_id=current_user.id
    )
    db.add(first_message)
    
    await db.commit()
    await db.refresh(new_chat)
    
    return new_chat



@router.post("/{chat_id}/message", response_model=schemas.Message, status_code=status.HTTP_201_CREATED, summary="Create a new message in chat")
async def create_new_message(
    chat_id: int,
    mess_content: schemas.MessageCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Add a new message to a chat.
        - **chat_id**: ID of the chat.
        - **mess_content**: Content of the new message.
    """
    new_message = models.Message(
        sender_id = current_user.id,
        chat_id = chat_id,
        content = mess_content.content
    )
    
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    
    return new_message
    

@router.delete("/{chat_id}", status_code=status.HTTP_201_CREATED, summary="Delete a chat by id")
async def delete_chat(
    chat_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Deletes a chat by its ID.
        -**chat_id**: The ID of the chat to delete.
    """
    result = await db.execute(
        select(models.Chat).where(
            models.Chat.id == chat_id,
            models.User.id == current_user.id
        )
    )
    chat_to_delete = result.scalars().first()
    if not chat_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat nenalezen nebo nemáte oprávnění jej smazat."
        )

    await db.delete(chat_to_delete)
    await db.commit()

    return None


@router.patch("/{chat_id}/rename", response_model = schemas.ChatResponse, status_code=status.HTTP_200_OK, summary="Rename a chat")
async def rename_chat(
    chat_id: int,
    new_name: schemas.RenameName,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Rename a chat.
        - **chat_id**: ID of the chat to rename.
        - **new_name**: New name for the chat.
    """
    result = await db.execute(
        select(models.Chat).where(
            models.Chat.id == chat_id,
            models.Chat.user_id == current_user.id
        )
    )
    chat_to_rename = result.scalars().first()

    if not chat_to_rename:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat nenalezen nebo nemáte oprávnění jej přejmenovat."
        )

    chat_to_rename.name = new_name.name
    db.add(chat_to_rename)
    await db.commit()
    await db.refresh(chat_to_rename)

    return chat_to_rename



@router.post("/{chat_id}/agents/{agent_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.ChatResponse, summary="Add agent to chat")
async def add_agent_to_chat(
    chat_id: int,
    agent_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """ 
        Add an agent to a chat.
        -**chat_id**: ID of the chat.
        -**agent_id**: ID of the agent.
    """
    result = await db.execute(
        select(models.Chat).options(selectinload(models.Chat.agents))
        .where(models.Chat.id == chat_id, models.Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    agent = await db.get(models.Agent, agent_id)
    if not agent or agent.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    if agent in chat.agents:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Agent is already in this chat")

    chat.agents.append(agent)
    await db.commit()
    await db.refresh(chat)
    
    return chat


@router.delete("/{chat_id}/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete agent from the chat")
async def remove_agent_from_chat(
    chat_id: int,
    agent_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Delete an agent from the chat.
        -**chat_id**: ID of the chat.
        -**agent_id**: ID of the agent.
    """
    result = await db.execute(
        select(models.Chat).options(selectinload(models.Chat.agents))
        .where(models.Chat.id == chat_id, models.Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    agent_to_remove = next((agent for agent in chat.agents if agent.id == agent_id), None)
    
    if not agent_to_remove:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found in this chat")

    chat.agents.remove(agent_to_remove)
    await db.commit()

    return None 


@router.get("/{chat_id}/agents/", response_model=List[schemas.AgentResponse], summary="Get all agents for the chat")
async def get_agents_in_chat(
    chat_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """ 
        Get all agents for the chat.
        -**chat_id**: ID for the chat.
    """
    result = await db.execute(
        select(models.Chat).options(
            selectinload(models.Chat.agents).selectinload(models.Agent.model_ai)
        )
        .where(models.Chat.id == chat_id, models.Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    response_agents = []
    for agent in chat.agents:
        response_agents.append(
            schemas.AgentResponse(
                id=agent.id,
                name=agent.name,
                prompt=agent.prompt,
                code=agent.code,
                model_ai_name=agent.model_ai.name if agent.model_ai else "Neznámý model"
            )
        )
        
    return response_agents


@router.get("/{chat_id}", summary="Get chat by ID")
async def get_chat(
    chat_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Get a chat by ID.
        - **chat_id**: ID of the chat.
        - Returns chat ID, graph ID, and name.
    """
    chat = await db.get(models.Chat, chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {
        "id": chat.id,
        "graph_id": chat.graph_id,
        "name": chat.name
    }