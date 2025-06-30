from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, List, Dict, Optional, Any, Annotated
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import models
from ..config import OPENAI_API_KEY
import os
import uuid

# Vytvoříme složku pro ukládání checkpointů
os.makedirs("checkpoints", exist_ok=True)
memory = SqliteSaver.from_conn_string("checkpoints/mas.db")

class AgentMessage(TypedDict):
    """Zpráva v konverzaci s agentem"""
    role: str  # "user" nebo "assistant"
    content: str  # Obsah zprávy
    agent_id: Optional[int]  # ID agenta, který vytvořil zprávu (pouze pro role="assistant")
    agent_name: Optional[str]  # Jméno agenta, který vytvořil zprávu

class MASState(TypedDict):
    """Stav multiagentového systému"""
    messages: Annotated[List[AgentMessage], add_messages]  # Historie zpráv
    chat_id: int  # ID chatu
    current_agent_id: Optional[int]  # ID aktuálního agenta
    final_answer: Optional[str]  # Finální odpověď od supervizora
    analysis: Optional[Dict[str, Any]]  # Analýza vstupu (pro supervizor)
    agent_responses: Optional[Dict[int, str]]  # Odpovědi jednotlivých agentů

class MultiAgentSystem:
    def __init__(self):
        """Inicializace multiagentového systému"""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY není nastaven")
        
        # Výchozí model pro agenty
        self.default_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            api_key=OPENAI_API_KEY
        )
        
        # Cache pro grafy podle ID chatu
        self.graph_cache = {}

    async def get_chat_agents(self, chat_id: int, db: AsyncSession) -> List[models.Agent]:
        """Získá všechny agenty pro daný chat"""
        query = select(models.Agent).join(
            models.ChatAgentLink,
            models.ChatAgentLink.agent_id == models.Agent.id
        ).where(models.ChatAgentLink.chat_id == chat_id)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_chat_history(self, chat_id: int, db: AsyncSession, limit: int = 20) -> List[models.Message]:
        """Získá historii zpráv z chatu"""
        query = select(models.Message).where(
            models.Message.chat_id == chat_id
        ).order_by(models.Message.timestamp).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    def create_agent_node(self, agent_id: int, agent_name: str, prompt: str, model_identifier: str = None):
        """Vytvoří funkci uzlu pro agenta v grafu"""
        
        def agent_node(state: MASState) -> MASState:
            # Vytvoření LLM instance podle modelu agenta
            llm = self.default_llm if not model_identifier else ChatOpenAI(
                model=model_identifier,
                temperature=0.2,
                api_key=OPENAI_API_KEY
            )
            
            # Příprava historie zpráv pro kontext
            messages = []
            for msg in state["messages"]:
                if msg["role"] == "user":
                    messages.append({"role": "user", "content": msg["content"]})
                else:
                    # Pro zprávy od agentů přidáme, který agent to byl
                    agent_info = f" (Agent: {msg['agent_name']})" if msg.get("agent_name") else ""
                    messages.append({"role": "assistant", "content": msg["content"] + agent_info})
            
            # Příprava promptu s instrukcemi pro agenta
            system_message = {
                "role": "system", 
                "content": prompt or f"Jsi agent '{agent_name}'. Odpovídej na otázky uživatele."
            }
            
            # Získání odpovědi od LLM
            response = llm.invoke([system_message] + messages)
            
            # Uložení odpovědi agenta
            agent_responses = state.get("agent_responses", {})
            agent_responses[agent_id] = response.content
            
            return {
                **state,
                "agent_responses": agent_responses,
                "current_agent_id": agent_id
            }
        
        return agent_node

    def create_supervisor_node(self, agents: List[models.Agent]):
        """Vytvoří funkci uzlu pro supervizora"""
        
        def supervisor_node(state: MASState) -> MASState:
            # Pokud nejsou žádné odpovědi od agentů, vrátíme původní stav
            if not state.get("agent_responses"):
                return state
            
            # Příprava odpovědí od agentů pro supervizora
            agent_responses_text = "\n\n".join([
                f"### Agent {agents[i].name}:\n{response}" 
                for i, (agent_id, response) in enumerate(state["agent_responses"].items())
            ])
            
            # Získání poslední zprávy uživatele
            last_user_message = next((msg["content"] for msg in reversed(state["messages"]) 
                                     if msg["role"] == "user"), "")
            
            # Prompt pro supervizora
            system_prompt = """
            Jsi supervizor, který koordinuje odpovědi od několika agentů.
            Tvým úkolem je:
            1. Analyzovat odpovědi od všech agentů
            2. Vybrat nejlepší odpověď nebo zkombinovat odpovědi do jedné koherentní
            3. Poskytnout finální, ucelenou odpověď na dotaz uživatele
            
            Odpověz přímo na dotaz uživatele na základě informací od agentů.
            """
            
            user_prompt = f"""
            Dotaz uživatele: {last_user_message}
            
            Odpovědi agentů:
            {agent_responses_text}
            
            Tvá finální odpověď:
            """
            
            # Získání odpovědi od supervizora
            response = self.default_llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # Vytvoření zprávy od supervizora
            return {
                **state,
                "final_answer": response.content,
                "messages": state["messages"] + [{
                    "role": "assistant",
                    "content": response.content,
                    "agent_id": None,
                    "agent_name": "Supervisor"
                }]
            }
        
        return supervisor_node

    def create_router_node(self, agents: List[models.Agent]):
        """Vytvoří router funkci, která rozhoduje, kterému agentovi předat dotaz"""
        
        def router_node(state: MASState) -> Dict:
            # V supervizor workflow pošleme vstupy všem agentům
            return {"next": [agent.name for agent in agents]}
        
        return router_node

    async def build_agent_graph(self, chat_id: int, agents: List[models.Agent]) -> StateGraph:
        """Vytvoří graf LangGraph pro multiagentový systém"""
        builder = StateGraph(MASState)
        
        # Přidání uzlů pro všechny agenty
        for agent in agents:
            # Získání identifikátoru modelu, pokud existuje
            model_identifier = None
            if agent.model_ai and agent.model_ai.model_identifier:
                model_identifier = agent.model_ai.model_identifier
            
            builder.add_node(
                agent.name,
                self.create_agent_node(
                    agent_id=agent.id,
                    agent_name=agent.name,
                    prompt=agent.prompt,
                    model_identifier=model_identifier
                )
            )
        
        # Přidání uzlu pro supervizora
        builder.add_node("supervisor", self.create_supervisor_node(agents))
        
        # Přidání uzlu pro router
        builder.add_node("router", self.create_router_node(agents))
        
        # Nastavení toku grafu: START -> router -> agenti -> supervisor -> END
        builder.add_edge(START, "router")
        
        # Podmíněné hrany z routeru do agentů
        builder.add_conditional_edges(
            "router",
            lambda state: {"next": state.get("next", [])},
            {agent.name: agent.name for agent in agents}
        )
        
        # Hrany od agentů k supervizorovi
        for agent in agents:
            builder.add_edge(agent.name, "supervisor")
        
        builder.add_edge("supervisor", END)
        
        # Kompilace grafu
        graph = builder.compile(checkpointer=memory)
        
        # Uložení grafu do cache
        self.graph_cache[chat_id] = graph
        
        return graph

    async def process_message(self, chat_id: int, message: str, user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Zpracuje zprávu v chatu a získá odpověď od MAS"""
        # Získání agentů pro tento chat
        agents = await self.get_chat_agents(chat_id, db)
        if not agents:
            return {"error": "Pro tento chat nejsou konfigurováni žádní agenti"}
        
        # Získání historie konverzace
        history = await self.get_chat_history(chat_id, db)
        
        # Příprava zpráv pro graf
        messages = []
        for msg in history:
            if msg.sender_id:
                # Zpráva od uživatele
                messages.append({
                    "role": "user",
                    "content": msg.content,
                    "agent_id": None,
                    "agent_name": None
                })
            else:
                # Zpráva od agenta
                agent_name = None
                if msg.agent_id:
                    # Pokud existují vazby mezi zprávami a agenty, našli bychom jméno agenta
                    agent_name = "Agent"  # Zjednodušení pro prototyp
                
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "agent_id": msg.agent_id,
                    "agent_name": agent_name
                })
        
        # Přidání aktuální zprávy
        messages.append({
            "role": "user",
            "content": message,
            "agent_id": None,
            "agent_name": None
        })
        
        # Příprava počátečního stavu
        initial_state = MASState(
            messages=messages,
            chat_id=chat_id,
            current_agent_id=None,
            final_answer=None,
            analysis=None,
            agent_responses={}
        )
        
        # Získání nebo vytvoření grafu pro tento chat
        if chat_id not in self.graph_cache:
            graph = await self.build_agent_graph(chat_id, agents)
        else:
            graph = self.graph_cache[chat_id]
        
        # Konfigurace pro běh grafu
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Spuštění grafu
            final_state = await graph.ainvoke(initial_state, config=config)
            
            # Uložení zprávy uživatele do databáze
            user_message = models.Message(
                chat_id=chat_id,
                sender_id=user_id,
                content=message
            )
            db.add(user_message)
            
            # Uložení odpovědi multiagentového systému
            if final_state.get("final_answer"):
                agent_message = models.Message(
                    chat_id=chat_id,
                    sender_id=None,  # Null = zpráva od systému
                    content=final_state["final_answer"]
                )
                db.add(agent_message)
            
            # Commit změn do databáze
            await db.commit()
            
            # Vrácení výsledku
            return {
                "user_message": message,
                "mas_response": final_state.get("final_answer", ""),
                "agent_responses": final_state.get("agent_responses", {})
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"Chyba při zpracování zprávy: {str(e)}"}

    async def stream_agent_updates(self, chat_id: int, message: str, user_id: int, db: AsyncSession):
        """Stream aktualizací při běhu agentního systému"""
        # Podobná logika jako process_message, ale s použitím astream místo ainvoke
        agents = await self.get_chat_agents(chat_id, db)
        if not agents:
            yield {"error": "Pro tento chat nejsou konfigurováni žádní agenti"}
            return
        
        # Získání historie a příprava dat podobně jako v process_message
        history = await self.get_chat_history(chat_id, db)
        messages = []
        for msg in history:
            if msg.sender_id:
                messages.append({
                    "role": "user",
                    "content": msg.content,
                    "agent_id": None,
                    "agent_name": None
                })
            else:
                agent_name = None
                if msg.agent_id:
                    agent_name = "Agent"
                
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "agent_id": msg.agent_id,
                    "agent_name": agent_name
                })
        
        messages.append({
            "role": "user",
            "content": message,
            "agent_id": None,
            "agent_name": None
        })
        
        initial_state = MASState(
            messages=messages,
            chat_id=chat_id,
            current_agent_id=None,
            final_answer=None,
            analysis=None,
            agent_responses={}
        )
        
        if chat_id not in self.graph_cache:
            graph = await self.build_agent_graph(chat_id, agents)
        else:
            graph = self.graph_cache[chat_id]
        
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Uložení zprávy uživatele do databáze
            user_message = models.Message(
                chat_id=chat_id,
                sender_id=user_id,
                content=message
            )
            db.add(user_message)
            await db.commit()
            
            # Streamování aktualizací z grafu
            current_state = initial_state.copy()
            async for update in graph.astream(initial_state, config=config):
                # Aktualizace stavu
                current_state.update(update)
                
                # Určení aktuálního kroku a stavu
                current_node = graph.get_state(config=config).get("current_node")
                
                if current_node in [agent.name for agent in agents]:
                    # Agent pracuje
                    yield {
                        "status": "processing",
                        "agent": current_node,
                        "message": f"Agent {current_node} pracuje na odpovědi..."
                    }
                elif current_node == "supervisor":
                    # Supervisor pracuje
                    yield {
                        "status": "processing",
                        "agent": "Supervisor",
                        "message": "Supervisor kompiluje odpovědi...",
                        "agent_responses": current_state.get("agent_responses", {})
                    }
                
                if current_state.get("final_answer"):
                    # Finální odpověď je připravena
                    agent_message = models.Message(
                        chat_id=chat_id,
                        sender_id=None,
                        content=current_state["final_answer"]
                    )
                    db.add(agent_message)
                    await db.commit()
                    
                    yield {
                        "status": "complete",
                        "message": current_state["final_answer"],
                        "agent_responses": current_state.get("agent_responses", {})
                    }
                    
            # Pokud by nebylo odesláno finale
            if not current_state.get("final_answer"):
                yield {
                    "status": "error",
                    "message": "Nepodařilo se získat odpověď od systému"
                }
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield {"error": f"Chyba při streamování odpovědi: {str(e)}"}


# Vytvoření globální instance MAS
mas = MultiAgentSystem()