from fastapi import FastAPI, WebSocket, Depends, HTTPException, BackgroundTasks, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from .db.schemas import AgentState
from .db.database import get_db
from .db.models import AgentSession
# from .agent import Agent # Odebrání starého agenta
import json
import uuid # Pro generování unikátních thread_id

app = FastAPI(title="Agent System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance LangGraphAgenta
lang_agent = LangGraphAgent()

@app.get("/")
async def read_root():
    return {"message": "Agent System API"}

@app.post("/run-agent/", response_model=AgentState)
async def run_agent_endpoint(state: AgentState, db: AsyncSession = Depends(get_db)): # Přejmenováno pro srozumitelnost
    """Spouští agenta s daným stavem pomocí LangGraph"""
    try:
        initial_state_dict = state.dict()
        thread_id = str(uuid.uuid4()) # Unikátní ID pro tento běh grafu
        
        # Použití asynchronní metody z LangGraphAgenta
        final_graph_state_dict = await lang_agent.run_graph_async(initial_state_dict, thread_id)
        
        result_state = AgentState(**final_graph_state_dict)

        db_session = AgentSession(
            task=result_state.task, # Použijeme task z finálního stavu, pokud se může měnit
            state=result_state.dict()
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        
        return result_state
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(e)}")

@app.get("/result/{session_id}", response_class=HTMLResponse)
async def get_html_result(session_id: int, db: AsyncSession = Depends(get_db)):
    db_session = await db.get(AgentSession, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Předpokládáme, že db_session.state je dict, který odpovídá AgentState
    state_data = db_session.state if isinstance(db_session.state, dict) else json.loads(db_session.state)
    state = AgentState(**state_data)
    return state.html_content

@app.websocket("/ws/agent/")
async def websocket_endpoint(websocket: WebSocket): # Odebráno BackgroundTasks, pokud není explicitně potřeba pro stream
    """WebSocket endpoint pro průběžné aktualizace stavu agenta s LangGraph"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            initial_state = AgentState(**data)
            initial_state_dict = initial_state.dict()
            
            thread_id = str(uuid.uuid4()) # Unikátní ID pro tento WebSocket stream

            # Streamování aktualizací z LangGraph
            # accumulated_state pro sledování celkového stavu, pokud je potřeba
            current_accumulated_state = initial_state_dict.copy()
            node_count = 0 # Jednoduchý progress tracker

            async for update_chunk in lang_agent.stream_graph_updates_async(initial_state_dict, thread_id):
                node_count += 1
                # update_chunk je slovník, kde klíč je název uzlu a hodnota je výstup uzlu
                # Např.: {'query_builder': {'queries': ['dotaz1']}}
                
                # Aktualizace akumulovaného stavu
                for node_name, node_output in update_chunk.items():
                    if isinstance(node_output, dict):
                         current_accumulated_state.update(node_output)

                await websocket.send_json({
                    "status": f"Uzel '{list(update_chunk.keys())[0]}' dokončen.",
                    "progress": int((node_count / len(lang_agent.graph.nodes)) * 95) if lang_agent.graph.nodes else 50, # Hrubý odhad progresu
                    "intermediate_data": update_chunk 
                })
            
            # Po dokončení streamu získáme finální stav (pokud je potřeba explicitně)
            # final_graph_state_dict = await lang_agent.graph.aget_state(config={"configurable": {"thread_id": thread_id}})
            # final_state_for_client = AgentState(**final_graph_state_dict.values).dict()
            # Pro jednoduchost použijeme current_accumulated_state, který by měl být aktuální
            
            await websocket.send_json({
                "status": "Hotovo!", 
                "progress": 100, 
                "result": current_accumulated_state
            })
            
    except WebSocketDisconnect:
        print(f"WebSocket client disconnected: {websocket.client_state}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        await websocket.send_json({"error": str(e)})
        # Zvažte, zda zavřít spojení při chybě
        # await websocket.close(code=1011) 
        
        
        
        
        
        
        
        
        
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chats, agents

app = FastAPI(title="Multi-Agent System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Připojení routerů
app.include_router(chats.router)
app.include_router(agents.router)

@app.get("/")
async def root():
    return {"message": "MAS Agent System API"}