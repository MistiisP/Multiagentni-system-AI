import json
from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import time

from ..services.langgraph_builder import build_langgraph_from_db
from ..db.database import get_db
from ..db import models
from langchain_core.messages import HumanMessage

router = APIRouter()


@router.websocket("/ws/run-graph/{graph_id}", )
async def websocket_run_graph(
    websocket: WebSocket,
    graph_id: int,
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
        WebSocket endpoint for executing a LangGraph workflow.
        - **graph_id**: ID of the graph to execute.
        - **chat_id**: ID of the chat session.
        - **WebSocket connection required.**
        - Receives initial user messages and streams execution steps, audit logs, and final results to the client in real time.
        - Sends:
            - The graph structure as JSON (`type: "graph_json"`).
            - Each flow step as it occurs (`type: "flow_step"`).
            - Audit entries for each node execution (`type: "audit_entry"`).
            - Final answer and execution path at the end of the run (`type: "stream_end"`).
            - Error messages if an exception occurs (`type: "error"`).
        - At the end, saves the execution log and final answer to the database.
    """
    
    await websocket.accept()

    start_time = time.time()
    execution_log = {
        "execution_path": [],
        "node_outputs": {},
        "manager_decisions": [],  
        "audit_trail": [], #details logs
        "flow_steps": [] #from->to
    }

    total_tokens = 0
    final_content = ""
    last_node_name = "start"
    final_content = None

    try:
        graph, langgraph_json, manager_name = await build_langgraph_from_db(graph_id, db)
        await websocket.send_json({"type": "graph_json", "data": langgraph_json})
    
        initial_data = await websocket.receive_json()
        user_messages = initial_data.get("input_messages", [])

        state = {
            "messages": [HumanMessage(content=msg) for msg in user_messages],
            "current_task": user_messages[-1],
            "manager_trace": [],
            "flow_steps": []
        }

        async for event in graph.astream(state):
            node_name = list(event.keys())[0]
            if node_name.startswith("__"):
                continue

            node_output = event[node_name]
            execution_log["execution_path"].append(node_name)

            if last_node_name != "start":
                flow_step = {
                    "type": "flow_step",
                    "from": last_node_name,
                    "to": node_name,
                    "timestamp": datetime.now().isoformat()
                }
                execution_log["flow_steps"].append(flow_step)
                await websocket.send_json(flow_step)
            last_node_name = node_name

            audit_log_data = node_output.get("audit_log", {})
            input_data = audit_log_data.get("input", "N/A")
            output_data = audit_log_data.get("output", "N/A")
            
            
            
            print(f"[DEBUG RUN] Node: {node_name}")
            print(f"  -> audit_log_data: {audit_log_data}")
            print(f"  -> input_data: {input_data}")
            print(f"  -> output_data: {output_data}")
            
            message_content = ""
            if "messages" in node_output and node_output["messages"]:
                last_message = node_output["messages"][-1]
                message_content = getattr(last_message, "content", str(last_message))

            if output_data == "N/A" and message_content:
                output_data = message_content

            duration = node_output.get("duration_ms", 0) or 0
            tokens = node_output.get("tokens_used", 0) or 0
            started_at = node_output.get("started_at")
            ended_at = node_output.get("ended_at")

            total_tokens += int(tokens or 0)
            final_content = message_content

            audit_entry = {
                "agent": node_name,
                "duration_ms": duration,
                "tokens_used": tokens,
                "input": str(input_data),
                "output": str(output_data)[:600] if output_data else "N/A",
                "started_at": started_at,
                "ended_at": ended_at,
                "timestamp": datetime.now().isoformat()
            }
            execution_log["audit_trail"].append(audit_entry)

            await websocket.send_json({
                "type": "audit_entry",
                "data": audit_entry,
                "execution_path": execution_log["execution_path"]
            })

            execution_log["node_outputs"][node_name] = {
                "content": message_content,
                "timestamp": audit_entry["timestamp"],
                "started_at": started_at,
                "ended_at": ended_at,
                "duration_ms": duration,
                "tokens_used": tokens,
            }

            if "manager_trace" in node_output:
                execution_log["manager_decisions"] = node_output["manager_trace"]
                
            if node_name == manager_name and "messages" in node_output:
                last_message = node_output["messages"][-1]

                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    tool_call = last_message.tool_calls[0]

                    if tool_call.get("name") == "finish_task":
                        raw_args = tool_call.get("args", {})

                        if isinstance(raw_args, str):
                            try:
                                raw_args = json.loads(raw_args)
                            except Exception:
                                raw_args = {"__arg1": raw_args}

                        final_content = (
                            raw_args.get("final_answer") or
                            raw_args.get("__arg1") or
                            getattr(last_message, "content", "")
                        )

        total_duration = int((time.time() - start_time) * 1000)
        await websocket.send_json({
            "type": "stream_end",
            "path": execution_log["execution_path"],
             "final_answer": final_content
        })

        if execution_log["node_outputs"]:
            log_entry = models.GraphExecutionLog(
                chat_id=chat_id,
                graph_id=graph_id,
                execution_path=execution_log["execution_path"],
                node_outputs=execution_log["node_outputs"],
                manager_decisions=execution_log["manager_decisions"],
                total_duration_ms=total_duration,
                tokens_used=total_tokens,
                audit_trail=execution_log["audit_trail"],
                flow_steps=execution_log["flow_steps"]
            )
            db.add(log_entry)
            
            if final_content:
                message = models.Message(
                    chat_id=chat_id,
                    sender_id=None,
                    content=final_content
                )
                db.add(message)

            try:
                await db.commit()
            except Exception as e:
                await db.rollback()

    except Exception as e:
        await websocket.send_json({"type": "error", "data": str(e)})
        raise
    finally:
        await websocket.close()
