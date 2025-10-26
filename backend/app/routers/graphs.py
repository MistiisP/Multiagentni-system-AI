from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select, insert
from typing import List
from pydantic import BaseModel

from ..db import database, models, schemas
from ..services.auth import get_current_user

router = APIRouter(
    prefix="/graphs",
    tags=["graphs"]
)

@router.get("/", summary="Get list of graphs for current user")
async def get_user_graphs(
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Get list of graphs.
        -**Authentication required.**
        - Returns a list of graphs (ID and name) that the user has access to.
    """
    stmt = (
        select(models.Graph)
        .join(models.Chat, models.Chat.graph_id == models.Graph.id)
        .where(models.Chat.user_id == current_user.id)
        .distinct()
    )
    result = await db.execute(stmt)
    graphs = result.scalars().all()
    
    return [{"id": graph.id, "name": graph.name} for graph in graphs]



@router.get("/{graph_id}/visualize", summary="Get graph for visualization")
async def get_graph_for_visualization(
    graph_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Get a graph's structure for visualization.
        - **graph_id**: ID of the graph to visualize.
        - **Authentication required.**
        - Returns all nodes (with agent names) and edges (with conditions) for the graph.
    """
    stmt = (
        select(models.Graph)
        .options(
            selectinload(models.Graph.nodes).selectinload(models.Node.agent),
            selectinload(models.Graph.edges).selectinload(models.Edge.from_node),
            selectinload(models.Graph.edges).selectinload(models.Edge.to_node)
        )
        .where(models.Graph.id == graph_id)
    )
    result = await db.execute(stmt)
    graph = result.unique().scalar_one_or_none()

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    nodes_for_fe = []
    for node in graph.nodes:
        nodes_for_fe.append({
            "id": str(node.id),
            "data": {"label": node.agent.name if node.agent else "Special Node"},
            "position": {"x": 0, "y": 0}
        })

    edges_for_fe = []
    for edge in graph.edges:
        if edge.from_node and edge.to_node:
            edge_dict = {
                "id": f"e{edge.from_node.id}-{edge.to_node.id}",
                "source": str(edge.from_node.id),
                "target": str(edge.to_node.id),
            } 
            if edge.condition:
                edge_dict["label"] = edge.condition
            edges_for_fe.append(edge_dict)
    
    print(nodes_for_fe)
    print(edges_for_fe)
    return {"nodes": nodes_for_fe, "edges": edges_for_fe}






@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a non-linear graph from visual editor")
async def create_full_graph(
    graph_data: schemas.FullGraphCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        Create a new graph (workflow) for a chat.
        - **graph_data**: Structure of the graph (nodes, edges, entry node, etc.).
        - If a graph already exists for the chat, it will be deleted and replaced.
    """
    chat = await db.get(models.Chat, graph_data.chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.graph_id:
        old_graph = await db.get(models.Graph, chat.graph_id)
        if old_graph:
            await db.delete(old_graph)
            await db.flush()

    new_graph = models.Graph(name=f"Workflow pro Chat {graph_data.chat_id}")
    db.add(new_graph)
    await db.flush()

    node_id_map = {}
    db_nodes = []
    for node_data in graph_data.nodes:
        new_node = models.Node(agent_id=node_data.agent_id)
        db.add(new_node)
        db_nodes.append(new_node)
    await db.flush()

    for i, node_data in enumerate(graph_data.nodes):
        node_id_map[node_data.id_in_graph] = db_nodes[i].id

    for node in db_nodes:
        await db.execute(
            insert(models.GraphNodeLink).values(graph_id=new_graph.id, node_id=node.id)
        )

    for edge_data in graph_data.edges:
        from_node_db_id = node_id_map.get(edge_data.from_node_id_in_graph)
        to_node_db_id = node_id_map.get(edge_data.to_node_id_in_graph)
        if from_node_db_id is None or to_node_db_id is None:
            raise HTTPException(status_code=400, detail="Invalid node ID in edge definition")
        new_edge = models.Edge(
            from_node_id=from_node_db_id,
            to_node_id=to_node_db_id,
            condition=edge_data.condition,
            graph_id=new_graph.id
        )
        db.add(new_edge)

    entry_node_db_id = node_id_map.get(graph_data.entry_node_id_in_graph)
    if entry_node_db_id is None:
        raise HTTPException(status_code=400, detail="Entry node not found")

    new_graph.entry_node_id = entry_node_db_id
    chat.graph_id = new_graph.id

    await db.commit()
    return {"message": "Graf byl vytvořen", "graph_id": new_graph.id}