/*
 * React component for visually building and editing a workflow graph of agents assigned to a chat.
 * Purpose:
 * - Allows users to visually connect agents, set the entry node, and define conditional branches between agents.
 * - Designed for workflow management in the context of a specific chat (identified by chatId).
 * Features:
 * - Displays agents as draggable nodes using ReactFlow.
 * - Users can connect nodes (agents) with edges to define workflow steps.
 * - Clicking a node sets it as the entry node (highlighted).
 * - Right-clicking an edge allows setting a condition (label) for branching.
 * - Users can remove edges by clicking on them.
 * - Handles saving the workflow graph to the backend (including nodes, edges, entry node, and chat association).
 * Usage:
 * - Place this component on a page where you want to allow users to build or edit a workflow for a chat.
 * - Requires a valid chatId prop.
 * - Should be used within context providers for agents, authentication, and graph state.
 * Props:
 * - chatId (number): The ID of the chat for which the workflow is being built.
 */
import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, { useNodesState, useEdgesState, addEdge, Background, BackgroundVariant, Controls, type OnConnect, type Node } from 'reactflow';
import 'reactflow/dist/style.css';
import { useGraph } from '../../services/graphContext';
import { useAgents } from '../../services/agentContext';
import { useAuth } from '../../services/authContext';

interface WorkflowBuilderProps {
  chatId: number;
}

const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({ chatId }) => {
  const { setGraphId } = useGraph();
  const { activeChatAgents } = useAgents();
  const { token } = useAuth();

  const [entryNode, setEntryNode] = useState<string | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initialNodes: Node[] = activeChatAgents.map((agent, index) => ({
      id: agent.id.toString(),
      type: 'default',
      data: { label: `${agent.name}`, agentId: agent.id },
      position: { x: 250, y: 100 * index },
      style: agent.id.toString() === entryNode ? { border: "2px solid #0066cc", color: "#0066cc"} : {},
    }));
    setNodes(initialNodes);
    setEdges([]);
    setEntryNode(null);
  }, [activeChatAgents, setNodes, setEdges]);


  const onConnect: OnConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, animated: true, type: 'default' }, eds)),
    [setEdges],
  );

  const onNodeClick = (_event: React.MouseEvent, node: Node) => {
    const newEntryNode = entryNode === node.id ? null : node.id;
    setEntryNode(newEntryNode);

    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        style: n.id === newEntryNode ? { border: '2px solid #0066cc', color: '#0066cc' } : {},
      }))
    );
  };


  const handleSaveGraph = async () => {
    setIsSubmitting(true);
    setError(null);

    if (!entryNode) {
        setError("Musíte zvolit počatečního agenta");
        setIsSubmitting(false);
        return;
    }

    const graphData = {
      chat_id: chatId,
      nodes: nodes.map(node => ({
        id_in_graph: node.id,
        agent_id: node.data.agentId,
      })),
      edges: edges.map(edge => ({
        from_node_id_in_graph: edge.source,
        to_node_id_in_graph: edge.target,
        condition: edge.label as string || null,
      })),
      entry_node_id_in_graph: entryNode,
    };

    try {
      const response = await fetch('http://127.0.0.1:8000/graphs/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(graphData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Nepodařilo se uložit graf.');
      }

      const data = await response.json();
      if (data.id) {
        setGraphId(data.id);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="workflow-builder">
      <h4>Správa WorkFlow</h4>
      <p>Vizuálně propojte agenty a vytvořte tak pracovní postup. Kliknutím na agenta zvolíte počáteční uzel. Pravýmm tlačítkem na hranu můžete nastavit podmínku pro větvení.</p>
      
      <div style={{ height: '400px', width: '100%', border: '1px solid #444', marginTop: '1rem' }}>
        <ReactFlow
            nodes={nodes} edges={edges}
            onNodesChange={onNodesChange} onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
            onEdgeClick={(_event, edge) => {
                setEdges((eds) => eds.filter((e) => e.id !== edge.id));
            }}
            onNodeClick={onNodeClick}

            onEdgeContextMenu={(event, edge) => {
                event.preventDefault();
                const condition = prompt('Zadejte podmínku pro tuto hranu (nechte prázdné pro odstranění):', edge.label as string || '');
                setEdges((eds) =>
                eds.map((e) => {
                    if (e.id === edge.id) {
                    return { ...e, label: condition || undefined };
                    }
                    return e;
                    })
                );
            }} >
          <Controls />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </div>

      <button onClick={handleSaveGraph} disabled={isSubmitting || nodes.length < 1} style={{marginTop: '1rem'}}>
        {isSubmitting ? 'Ukládám...' : 'Uložit graf'}
      </button>
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default WorkflowBuilder;