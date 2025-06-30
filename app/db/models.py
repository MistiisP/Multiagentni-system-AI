import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from .database import Base

# ---------------------------------------------------------------------------
# Modely pro běh agentů a ukládání výsledků
# ---------------------------------------------------------------------------

class AgentSession(Base):
    """Ukládá stav a výsledek jednoho konkrétního běhu agenta."""
    __tablename__ = "agent_sessions"
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, index=True)
    state = Column(JSON)  # Uložíme Pydantic model AgentState jako JSON

# ---------------------------------------------------------------------------
# Základní modely pro uživatele, autentizaci a chat
# ---------------------------------------------------------------------------

class User(Base):
    """Model pro uživatele systému."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    chats = relationship("Chat", back_populates="user")
    messages = relationship("Message", back_populates="sender")

class Chat(Base):
    """Model pro jednu chatovací konverzaci."""
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    agents = relationship("Agent", secondary="chat_agent_link", back_populates="chats")

class Message(Base):
    """Model pro jednu zprávu v chatu."""
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id")) # Může být NULL, pokud píše systém/agent
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")

# ---------------------------------------------------------------------------
# Modely pro definici a správu agentů (pro budoucí použití)
# ---------------------------------------------------------------------------

class Agent(Base):
    """Definice jednoho typu agenta (např. 'Doktor', 'Výzkumník')."""
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    prompt = Column(Text)
    model_ai_id = Column(Integer, ForeignKey("models_of_ai.id"))
    code = Column(Text, nullable=True)  # Kód agenta (např. Python funkce)
    
    model_ai = relationship("ModelOfAI", back_populates="agents")
    chats = relationship("Chat", secondary="chat_agent_link", back_populates="agents")

class ModelOfAI(Base):
    """Definice dostupných AI modelů (např. 'gpt-4o', 'claude-3-opus')."""
    __tablename__ = "models_of_ai"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False) # Např. "OpenAI GPT-4o"
    model_identifier = Column(String(255), nullable=True) # Např. "gpt-4o"
    created_at = Column(DateTime, server_default=func.now())
    
    agents = relationship("Agent", back_populates="model_ai")

class ChatAgentLink(Base):
    """Spojovací tabulka pro Many-to-Many vztah mezi Chat a Agent."""
    __tablename__ = "chat_agent_link"
    chat_id = Column(Integer, ForeignKey("chats.id"), primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), primary_key=True)


# ---------------------------------------------------------------------------
# Modely pro dynamickou definici grafů agentů (pro budoucí použití)
# ---------------------------------------------------------------------------

class Graph(Base):
    """Definice jednoho workflow (grafu) složeného z uzlů a hran."""
    __tablename__ = "graphs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    
    nodes = relationship("Node", secondary="graph_node_link", back_populates="graphs")
    edges = relationship("Edge", back_populates="graph", cascade="all, delete-orphan")

class Node(Base):
    """Definice jednoho uzlu v grafu (krok v procesu)."""
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    node_type = Column(String(100)) # Např. 'llm_call', 'tool_call', 'conditional'
    code_or_prompt = Column(Text, nullable=True)
    
    graphs = relationship("Graph", secondary="graph_node_link", back_populates="nodes")
    # Vztahy pro snadnou navigaci po hranách
    outgoing_edges = relationship("Edge", foreign_keys="Edge.from_node_id", back_populates="from_node", cascade="all, delete-orphan")
    incoming_edges = relationship("Edge", foreign_keys="Edge.to_node_id", back_populates="to_node", cascade="all, delete-orphan")

class Edge(Base):
    """Definice jedné hrany (spojení) mezi dvěma uzly v grafu."""
    __tablename__ = "edges"
    id = Column(Integer, primary_key=True, index=True)
    from_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    to_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    graph_id = Column(Integer, ForeignKey("graphs.id"), nullable=False)
    condition = Column(Text, nullable=True) # Podmínka pro přechod po hraně
    
    from_node = relationship("Node", foreign_keys=[from_node_id], back_populates="outgoing_edges")
    to_node = relationship("Node", foreign_keys=[to_node_id], back_populates="incoming_edges")
    graph = relationship("Graph", back_populates="edges")

class GraphNodeLink(Base):
    """Spojovací tabulka pro Many-to-Many vztah mezi Graph a Node."""
    __tablename__ = "graph_node_link"
    graph_id = Column(Integer, ForeignKey("graphs.id"), primary_key=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), primary_key=True)