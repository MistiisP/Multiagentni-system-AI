from datetime import datetime
import time
import os
import re
import inspect
from typing import TypedDict, List, Dict, Any, Sequence, Annotated, Optional
import operator
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain.callbacks.manager import get_openai_callback
from langchain.agents import create_tool_calling_agent, AgentExecutor
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from langchain_core.messages import ToolMessage

from ..db import models
from ..utils.tools import TOOL_IMPLEMENTATIONS

MAX_DELEGATIONS_PER_AGENT = 3
load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_task: str
    delegation_count: Dict[str, int]
    manager_trace: List[str]
    last_called_specialist: Optional[str]
    duration_ms: Annotated[Optional[int], operator.add]
    tokens_used: Annotated[Optional[int], operator.add]
    audit_log: Optional[Dict[str, str]]
    
def sanitize_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)


def get_llm_instance(agent: models.Agent):
    openai_model = next(
        (m for m in agent.models_ai if m.provider == "openai"),
        None
    )
    
    if openai_model:
        api_key = openai_model.api_key
        model_name = openai_model.model_identifier or "gpt-4o"
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = "gpt-4o"
    
    if not api_key:
        raise ValueError(f"Chybí API klíč pro model '{model_name}' u agenta '{agent.name}'.")
    
    return ChatOpenAI(model=model_name, api_key=api_key, temperature=0.1)


def create_specialist_node(agent_model: models.Agent, tools: List[Tool]):
    llm = get_llm_instance(agent_model)
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""Jsi specialista {agent_model.name}. Tvá role: {agent_model.prompt}. 
Použij dostupné nástroje k vyřešení zadaného úkolu a vrať výsledek. Můžeš jenom vyřešit svojí část úkolu.
Můžeš:
- Vyřešit jen svůj díl úkolu.
- Používat jen nástroje, které máš k dispozici.
- Vrátit výsledek své práce (data, analýza, text, kód…).

Máš zákazáno:
- Řešit celý úkol uživatele, pokud je to z jiné odbornosti, než kterou ovládáš.
- Ukončovat úkol (finish_task). To ty nemůžeš dělat.

VÝSTUP:
- Odpověď jen na zadaný sub-úkol.
- Stručná, věcná, v rámci tvé role.
- Pokud nemáš dost informací, tak napiš, co potřebuješ."""),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    async def node_func(state: AgentState) -> Dict[str, Any]:
        manager_ai_message = state["messages"][-1]
        tool_call = manager_ai_message.tool_calls[0]
        current_task = state.get("current_task", "")
        sub_args = tool_call.get("args", {})

        user_msg = HumanMessage(content=f"Hlavní úkol: {current_task}\n\nSub-úkol:\n{sub_args}")

        start_time = time.time()
        tokens_used = 0
        
        try:
            with get_openai_callback() as cb:
                result = await executor.ainvoke({"messages": [user_msg]})
                tokens_used = cb.total_tokens if cb else 0
        except Exception as e:
            print(f"Chyba '{agent_model.name}': {e}")
            output_content = f"Chyba: {str(e)}"
            tokens_used = 0
        else:
            output_content = str(result.get("output", "Dokončeno."))
            if tokens_used == 0:
                tokens_used = int(len(output_content.split()) * 1.3) # fallback odhad, počet slov * faktor
        
        duration_ms = int((time.time() - start_time) * 1000)

        log_input = sub_args.get("__arg1", sub_args)
        if isinstance(log_input, dict):
            log_input = ", ".join(f"{k}: {v}" for k, v in log_input.items())

        return {
            "messages": [ToolMessage(content=output_content, tool_call_id=tool_call['id'] )],
            "duration_ms": duration_ms,
            "tokens_used": tokens_used,
            "audit_log": {
                "input": str(log_input),
                "output": output_content
            }
        }
    return node_func


def create_manager_llm(agent_model: models.Agent, specialist_tools: List[Tool]):
    llm = get_llm_instance(agent_model)
    prompt = ChatPromptTemplate.from_messages([
        ("system", f""""Jsi {agent_model.name}, projektový manažer.
Tvým úkolem je řídit ostatní agenty (specialisty), rozdělit úkol na kroky a koordinovat jejich práci, dokud nebude finální výstup kompletní.

=========================
PRAVIDLA ROZHODOVÁNÍ:

1. Zanalyzuj původní úkol uživatele: {{current_task}}.
2. Rozděl úkol na logické dílčí kroky. Každý krok má být řešen jiným specialistou, pokud není logické dělat více kroků jedním.
3. Specialistům zadávej vždy pouze dílčí konkrétní úkol (např. "najdi studie", "vyhodnoť medicínsky", "převeď do HTML"), ne celý finální výstup.
4. Pokud ti specialista vrátí výsledek, zpracuj jej, ulož do kontextu a rozhodni, který další krok je potřeba.
5. Nikdy neukončuj úkol (finish_task), pokud:
   - nebyly dokončeny všechny logické kroky potřebné k finálnímu řešení,
   - nemáš ověřené výstupy (např. data → analýza → forma → finalizace).
6. Specialisté nemají vytvářet finální odpověď uživateli – pouze dílčí výsledky (data, analýza, návrh, kód, formátování…).
7. Finální odpověď generuj až tehdy, když máš všechny potřebné podklady.
8. Teprve poté zavolej finish_task a vrať hotový výstup.

=========================
Dostupní specialisté:
{{specialist_descriptions}}
=========================
"""),
        MessagesPlaceholder(variable_name="messages"),
    ])
    finish_tool = Tool(
        name="finish_task",
        description="Zavolej, když je úkol kompletně hotov a máš finální odpověď pro uživatele.",
        func=lambda final_answer: final_answer
    )
    all_tools = specialist_tools + [finish_tool]
    chain = prompt | llm.bind_tools(all_tools)
    return chain


def create_manager_router(manager_name: str, specialist_names: List[str]):
    def router_func(state: AgentState) -> str:
        last_message = state["messages"][-1]

        if isinstance(last_message, ToolMessage):
            return manager_name

        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            tool_name = last_message.tool_calls[0]['name']
            if tool_name in specialist_names:
                return tool_name
            if tool_name == "finish_task":
                return END
        
        return END
    return router_func


async def build_langgraph_from_db(graph_id: int, db: AsyncSession):
    """
        Build a LangGraph workflow from the database definition.
        - **graph_id**: ID of the graph to build.
        - Loads the graph structure, agents, and their models from the database.
        - Constructs a multi-agent workflow using the Manager-Specialist pattern:
            - The manager agent coordinates the workflow and delegates tasks to specialists.
            - Each specialist agent solves only its assigned sub-task using available tools.
        - Handles loop detection and prevents infinite delegation.
        - Returns:
            - The compiled LangGraph object (ready for execution).
            - The graph structure as JSON (nodes and edges for visualization).
            - The manager agent's name (entry point).
    """
    stmt = select(models.Graph).where(models.Graph.id == graph_id).options(
        selectinload(models.Graph.nodes).selectinload(models.Node.agent).selectinload(models.Agent.models_ai)
    )
    db_graph = (await db.execute(stmt)).unique().scalar_one_or_none()
    if not db_graph:
        raise ValueError(f"Graf s ID {graph_id} nebyl nalezen.")

    all_agents = [node.agent for node in db_graph.nodes if node.agent]
    entry_node = next((n for n in db_graph.nodes if n.id == db_graph.entry_node_id), None)
    if not entry_node or not entry_node.agent:
        raise ValueError("Vstupní uzel (Manager Agent) není v grafu definován.")

    manager_model = entry_node.agent
    manager_name = sanitize_name(manager_model.name)
    specialist_models = [agent for agent in all_agents if agent.id != manager_model.id]

    specialist_tools_for_delegation = []
    for agent in specialist_models:
        safe_name = sanitize_name(agent.name)
        specialist_tools_for_delegation.append(
            Tool(
                name=safe_name,
                description=f"Deleguje úkol na specialistu: {agent.name}. Role: {agent.prompt[:200]}",
                func=lambda x, _n=safe_name: x
            )
        )

    specialist_descriptions = "\n".join([
        f"- {sanitize_name(agent.name)}: {agent.prompt[:150]}"
        for agent in specialist_models
    ])

    builder = StateGraph(AgentState)

    manager_llm = create_manager_llm(manager_model, specialist_tools_for_delegation)

    async def manager_node(state: AgentState):
        messages = state["messages"]
        delegation_count = state.get("delegation_count", {}) or {}
        manager_trace = state.get("manager_trace", []) or []
        current_task = state.get("current_task", "")
        last_called_specialist = state.get("last_called_specialist", None)
        
        compact = []
        if messages and isinstance(messages[0], HumanMessage):
            compact.append(messages[0])
        i = 1
        while i < len(messages):
            msg = messages[i]
            
            if isinstance(msg, AIMessage) and msg.tool_calls:
                compact.append(msg)
                if i + 1 < len(messages) and isinstance(messages[i + 1], ToolMessage):
                    compact.append(messages[i + 1])
                    i += 2
                    continue
                else:
                    i += 1
            
            if isinstance(msg, (AIMessage, ToolMessage, HumanMessage)):
                compact.append(msg)
            
            i += 1
        
        if len(compact) > 20:
            compact = [compact[0]] + compact[-19:]
        
        specialist_outputs = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                source_tool_call_id = msg.tool_call_id
                source_ai_msg = next((m for m in reversed(messages) if isinstance(m, AIMessage) and m.tool_calls and m.tool_calls[0]['id'] == source_tool_call_id), None)
                specialist_name = source_ai_msg.tool_calls[0]['name'] if source_ai_msg else 'specialista'
                specialist_outputs.append(f"Výstup od '{specialist_name}': {msg.content[:300]}...")
        
        specialist_context = "\n".join(specialist_outputs) if specialist_outputs else "Zatím žádné výstupy od specialistů."

        deleg_info = "\n".join([f"- {name}: {count}x" for name, count in sorted(delegation_count.items())]) or "žádné"
        context_msg = SystemMessage(content=(
            f"==== SHRNUTÍ PŘEDCHOZÍ PRÁCE ====\n"
            f"KONTEXT VÝSTUPŮ OD SPECIALISTŮ:\n{specialist_context}\n\n"
            f"==== STAVOVÉ INFORMACE ====\n"
            f"Poslední volaný specialista: {last_called_specialist or 'žádný'}\n"
            f"Historie delegací:\n{deleg_info}\n\n"
            f"==== TVŮJ DALŠÍ KROK ====\n"
            f"Na základě kontextu a historie se rozhodni, jaký je další logický krok k dokončení úkolu: {current_task}."
        ))
        
        compact.append(context_msg)
    
        invoke_input = {
            "messages": compact,
            "current_task": current_task,
            "specialist_descriptions": specialist_descriptions
        }

        start_time = time.time()
        tokens_used = 0
        
        try:
            with get_openai_callback() as cb:
                result = await manager_llm.ainvoke(invoke_input)
                tokens_used = cb.total_tokens if cb else 0
        except Exception as e:
            print(f"CHYBA v manažerovi: {e}")
            result = AIMessage(content=f"Chyba v manažerovi: {str(e)}")
            tokens_used = 0
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        if tokens_used == 0 and isinstance(result, AIMessage):
            content_str = str(result.content)
            tokens_used = int(len(content_str.split()) * 1.3)
        
        new_delegation_count = dict(delegation_count)
        new_manager_trace = list(manager_trace)
        new_last_called = last_called_specialist

        if isinstance(result, AIMessage) and result.tool_calls:
            tool_name = result.tool_calls[0]['name']
            tool_args = result.tool_calls[0].get('args', {})
            
            if tool_name != "finish_task":
                print(f"[LOG] Delegating to specialist agent: {tool_name} with args: {tool_args}")
                new_delegation_count[tool_name] = new_delegation_count.get(tool_name, 0) + 1
                
                if new_delegation_count[tool_name] > MAX_DELEGATIONS_PER_AGENT:
                    loop_warning = (
                        f"Detekována možná smyčka: agent '{tool_name}' byl volán {new_delegation_count[tool_name]}x. "
                        f"Zvaž jiný postup nebo ukončení úkolu."
                    )
                    messages.append(SystemMessage(content=loop_warning))
                    new_manager_trace.append({"action": "loop_warning", "agent": tool_name, "message": loop_warning})

                    if new_delegation_count[tool_name] >= MAX_DELEGATIONS_PER_AGENT + 1:
                        return {
                            "messages": [AIMessage(content=f"Ukončeno kvůli opakující se smyčce agenta '{tool_name}'.")],
                            "delegation_count": new_delegation_count,
                            "manager_trace": new_manager_trace,
                            "last_called_specialist": tool_name,
                            "duration_ms": duration_ms,
                            "tokens_used": tokens_used,
                            "audit_log": {
                                "input": "Loop detection",
                                "output": f"Zastaveno po {new_delegation_count[tool_name]} volání agenta {tool_name}."
                            }
                        }
                
                
                new_manager_trace.append({      
                    "action": "delegate",
                    "to": tool_name,
                    "args": tool_args,
                    "timestamp": datetime.now().isoformat()
                })
                new_last_called = tool_name
            else:
                new_manager_trace.append("Manažer ukončil úkol (finish_task).")
        else:
            new_manager_trace.append("Manažer vrátil finální odpověď bez delegace.")
        
        audit_input = f"Úkol: {current_task}"
        
        if messages:
            last_msg = messages[-1]
            if isinstance(last_msg, ToolMessage):
                audit_input = f"Zpracovávám výstup od '{last_called_specialist}': {last_msg.content[:200]}..."
            elif isinstance(last_msg, HumanMessage):
                audit_input = f"Počáteční úkol od uživatele: {last_msg.content[:200]}"


        audit_output = "Finální odpověď."
        if isinstance(result, AIMessage) and result.tool_calls:
            tool_call = result.tool_calls[0]
            if tool_call['name'] == 'finish_task':
                audit_output = f"Finální odpověď: {tool_call.get('args', {}).get('final_answer', 'Dokončeno.')}"
            else:
                audit_output = f"Deleguji na: {tool_call['name']} s argumenty: {tool_call.get('args', {})}"
        elif isinstance(result, AIMessage) and result.content:
             audit_output = f"Odpověď manažera: {result.content}"

        print(f"[DEBUG MANAGER] audit_input = {audit_input}")
        print(f"[DEBUG MANAGER] audit_output = {audit_output}")


        return {
            "messages": [result],
            "delegation_count": new_delegation_count,
            "manager_trace": new_manager_trace,
            "last_called_specialist": new_last_called,
            "duration_ms": duration_ms,
            "tokens_used": tokens_used,
            "audit_log": {
                "input": audit_input,
                "output": audit_output
            }
        }

    builder.add_node(manager_name, manager_node)
    builder.set_entry_point(manager_name)

    for agent_model in specialist_models:
        agent_name = sanitize_name(agent_model.name)
        agent_tool_names = agent_model.tools if agent_model.tools else []
        
        agent_tools = []
        for tool_name in agent_tool_names:
            if tool_name not in TOOL_IMPLEMENTATIONS:
                print(f"CHYBA: Nástroj '{tool_name}' není definován.")
                continue
            
            tool_config = TOOL_IMPLEMENTATIONS[tool_name]
            required_provider = tool_config.get("required_provider")
            
            api_key = None
            if required_provider:
                matching_model = next(
                    (m for m in agent_model.models_ai if m.provider == required_provider),
                    None
                )
                if matching_model:
                    api_key = matching_model.api_key
                    print(f"[LOG] Agent '{agent_name}' používá model '{matching_model.name}' pro tool '{tool_name}'.")
                else:
                    print(f"VAROVÁNÍ: Agent '{agent_name}' nemá model pro '{required_provider}', použit .env fallback.")
                    api_key = os.getenv(f"{required_provider.upper()}_API_KEY")
            
            get_tool_func = tool_config["get_tool"]
            tool_args = {}
            if 'api_key' in inspect.signature(get_tool_func).parameters:
                tool_args["api_key"] = api_key
            
            try:
                tool_instance = get_tool_func(**tool_args)
                agent_tools.append(tool_instance)
                print(f"[LOG] Tool '{tool_name}' načten pro '{agent_name}'.")
            except Exception as e:
                print(f"CHYBA při načítání '{tool_name}' pro '{agent_name}': {e}")

        builder.add_node(agent_name, create_specialist_node(agent_model, agent_tools))

    router = create_manager_router(manager_name, [sanitize_name(a.name) for a in specialist_models])
    builder.add_conditional_edges(manager_name, router)
    for specialist in specialist_models:
        builder.add_edge(sanitize_name(specialist.name), manager_name)

    nodes = [{"id": n, "label": n} for n in builder.nodes]
    edges = []
    for source, target in builder.edges:
        edges.append({"source": str(source), "target": str(target)})
    for source, branch in builder.branches.items():
        for agent_model in specialist_models:
            edges.append({"source": source, "target": sanitize_name(agent_model.name)})
        edges.append({"source": source, "target": "END"})
    unique_edges = []
    seen = set()
    for e in edges:
        key = (e["source"], e["target"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)
    langgraph_json = {"nodes": nodes, "edges": unique_edges}

    langgraph = builder.compile()
     
    return langgraph, langgraph_json, manager_name
