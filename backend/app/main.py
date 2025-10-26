from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import agents, users, chats, ai_models, graphs, langgraph_run, tools, graphs_execution_log, auth

app = FastAPI(title="Multi-Agent System")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(chats.router)
app.include_router(ai_models.router)
app.include_router(graphs.router)
app.include_router(langgraph_run.router)
app.include_router(tools.router)
app.include_router(graphs_execution_log.router)

@app.get("/")
async def root():
    return {"message": "MAS Agent System API"}