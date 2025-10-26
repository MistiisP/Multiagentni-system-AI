/*
 * React component for visualizing a workflow graph structure for a given graph ID.
 * Purpose:
 * - Displays a directed graph (nodes and edges) representing the workflow structure associated with a specific graph.
 * Features:
 * - Fetches graph data (nodes and edges) from the backend using the provided graphId and user token.
 * - Automatically lays out nodes and edges using the dagre library for better readability (left-to-right).
 * - Renders the graph interactively using ReactFlow, including draggable nodes and arrow markers on edges.
 * Usage:
 * - Place this component where you want to visualize the workflow graph for a chat or agent.
 * - Requires a valid graphId and user authentication (token).
 * Props:
 * - graphId (number | null): The ID of the graph to visualize. If null, displays an info message.
 */
import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, { Controls, Background, applyNodeChanges, applyEdgeChanges,
type Node, type Edge, type OnNodesChange, type OnEdgesChange, MarkerType} from 'reactflow';
import 'reactflow/dist/style.css';
import { useAuth } from '../../services/authContext';
import dagre from 'dagre';

interface GraphVisualizerProps {
  graphId: number | null;
}

const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: 'LR' });

  const nodeWidth = 132;
  const nodeHeight = 36;

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};


const GraphVisualizer: React.FC<GraphVisualizerProps> = ({ graphId }) => {
  const { token } = useAuth();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const onNodesChange: OnNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const edgesWithArrow = edges.map(edge => ({
  ...edge, markerEnd:{type: MarkerType.ArrowClosed,},
  }));

  const fetchGraphData = useCallback(async () => {
    if (!graphId || !token) {
      setNodes([]);
      setEdges([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/graphs/${graphId}/visualize`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch graph data');
      }

      const data = await response.json();
      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(data.nodes, data.edges);

      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setNodes([]);
      setEdges([]);
    } finally {
      setIsLoading(false);
    }
  }, [graphId, token]);

  useEffect(() => {
    fetchGraphData();
  }, [fetchGraphData]);

  if (!graphId) {
    return <div className="info-text">Žádný graf není přiřazen k tomuto chatu.</div>;
  }

  if (isLoading) {
    return <div className="info-text">Načítám graf...</div>;
  }

  if (error) {
    return <div className="error-message">Chyba při načítání grafu: {error}</div>;
  }

  return (
    <>
    <h4>Vizualizace grafu</h4>
    <div style={{ marginTop:'1rem', height: '300px', width: '99%', border: '1px solid #555', borderRadius: '8px', background: '#1a1a1a', borderBottom:'1px solid #444' }}>
      <ReactFlow nodes={nodes} edges={edgesWithArrow} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} fitView proOptions={{ hideAttribution: true }}>
        <Controls />
        <Background />
      </ReactFlow>
    </div>
    </>
  );
};

export default GraphVisualizer;