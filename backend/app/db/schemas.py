from typing import List, Tuple, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


# User
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    

class User(BaseModel):
    id: int
    name: str
    email: EmailStr    

    class Config:
        from_attributes = True 
        



# Chats
class ChatPreview(BaseModel):
    id: int
    name: str
    last_message: str
    timestamp: str
    graph_id: Optional[int] = None
        
class ChatResponse(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime
    graph_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class Message(BaseModel):
    id: int
    chat_id: int
    sender_id: Optional[int] = None
    content: str

    class Config:
        from_attributes = True 

class MessageCreate(BaseModel):
    content: str
    
class RenameName(BaseModel):
    name: str
    
    class Config: 
        from_attributes = True
        
        
        
        
class ModelOfAIResponse(BaseModel):
    id: int
    name: str
    model_identifier: str

    class Config:
        from_attributes = True
        
        
# Agents
class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    model_ids: List[int]
    code: Optional[str] = None
    tools: Optional[List[str]] = None
    
    class Config: 
        from_attributes = True
    
class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    prompt: str
    models_ai: List[ModelOfAIResponse]
    tools: Optional[List[str]] = None
    code: Optional[str] = None
    
    class Config:
        from_attributes = True
        
class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    prompt: str | None = None
    model_ids: Optional[List[int]] = None
    tools: Optional[List[str]] = None
    code: str | None = None
               
    class Config:
        from_attributes = True





#AI models

class AIModelResponse(BaseModel):
    id: int
    name: str
    model_identifier: str

    class Config:
        from_attributes = True

class AIModelCreate(BaseModel):
    name: str
    model_identifier: str
    api_key: str


class AIModelUpdate(BaseModel):
    name: str | None = None
    model_identifier: str | None = None
    api_key: str | None = None




#Graphs
class NodeCreateData(BaseModel):
    id_in_graph: str
    agent_id: int

class EdgeCreateData(BaseModel):
    from_node_id_in_graph: str
    to_node_id_in_graph: str
    condition: Optional[str] = None

class FullGraphCreate(BaseModel):
    chat_id: int
    nodes: List[NodeCreateData]
    edges: List[EdgeCreateData]
    entry_node_id_in_graph: str


class GraphCreateRequest(BaseModel):
    chat_id: int
    agent_ids: List[int]