import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from .database import Base

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    chats = relationship("Chat", back_populates="user")
    messages = relationship("Message", back_populates="sender")
    agents = relationship("Agent", back_populates="user")
    ai_models =  relationship("ModelOfAI", back_populates="user")
    
    @classmethod
    def get_password_hash(cls, password):
        return pwd_context.hash(password)
    
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    graph_id = Column(Integer, ForeignKey("graphs.id", ondelete="SET NULL"), nullable=True)
    
    name = Column(String(50), nullable=False)
    
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    agents = relationship("Agent", secondary="chat_agent_link", back_populates="chats")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True) #null is AI answer/message
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")


class ModelOfAI(Base):
    __tablename__ = "models_of_ai"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255), nullable=False) 
    model_identifier = Column(String(255), nullable=True) 
    api_key = Column(String, nullable=True)
    
    agents = relationship("Agent", back_populates="model_ai")
    user = relationship("User", back_populates="ai_models")


class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_ai_id = Column(Integer, ForeignKey("models_of_ai.id"), nullable=True)
    
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(100), nullable=True) 
    prompt = Column(Text, nullable=True)
    
    tools = Column(JSON, nullable=True)
    code = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="agents")
    model_ai = relationship("ModelOfAI", back_populates="agents")
    chats = relationship("Chat", secondary="chat_agent_link", back_populates="agents")


class ChatAgentLink(Base):
    """ m:n chats:agents """
    __tablename__ = "chat_agent_link"
    chat_id = Column(Integer, ForeignKey("chats.id"), primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), primary_key=True)





class AgentSession(Base):
    __tablename__ = "agent_sessions"
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, index=True)
    state = Column(JSON)


class Graph(Base):
    __tablename__ = "graphs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    entry_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)
    
    nodes = relationship("Node", secondary="graph_node_link", back_populates="graphs", lazy="selectin")
    edges = relationship("Edge", back_populates="graph", cascade="all, delete-orphan", lazy="selectin")
    chat = relationship("Chat", backref="graph", uselist=False)



class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    agent = relationship("Agent")
    
    graphs = relationship("Graph", secondary="graph_node_link", back_populates="nodes", lazy="selectin")
    outgoing_edges = relationship("Edge", foreign_keys="Edge.from_node_id", back_populates="from_node", cascade="all, delete-orphan")
    incoming_edges = relationship("Edge", foreign_keys="Edge.to_node_id", back_populates="to_node", cascade="all, delete-orphan")



class Edge(Base):
    __tablename__ = "edges"
    id = Column(Integer, primary_key=True, index=True)
    from_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    to_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    graph_id = Column(Integer, ForeignKey("graphs.id"), nullable=False)
    condition = Column(Text, nullable=True) 
    
    from_node = relationship("Node", foreign_keys=[from_node_id], back_populates="outgoing_edges")
    to_node = relationship("Node", foreign_keys=[to_node_id], back_populates="incoming_edges")
    graph = relationship("Graph", back_populates="edges", lazy="selectin")


class GraphNodeLink(Base):
    """ m:n graphs:nodes """
    __tablename__ = "graph_node_link"
    graph_id = Column(Integer, ForeignKey("graphs.id"), primary_key=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), primary_key=True)
    
    
    
class GraphExecutionLog(Base):
    """ table for audit trail """
    __tablename__ = "graph_execution_logs"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    graph_id = Column(Integer, ForeignKey("graphs.id"))
    execution_timestamp = Column(DateTime, server_default=func.now())
    
    
    execution_path = Column(JSON)
    node_outputs = Column(JSON)
    manager_decisions = Column(JSON) 
    
    total_duration_ms = Column(Integer)
    tokens_used = Column(Integer, nullable=True)
    
    audit_trail = Column(JSON)
    flow_steps = Column(JSON)
    
    chat = relationship("Chat")
    graph = relationship("Graph")