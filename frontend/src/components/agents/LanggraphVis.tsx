/*
 * React component for visualizing the structure and execution path of a LangGraph workflow.
 * Purpose:
 * - Displays a directed graph (nodes and edges) representing the workflow structure.
 * - Highlights the execution path through the graph, showing which nodes and edges were traversed.
 * Features:
 * - Uses ReactFlow for interactive graph visualization.
 * - Automatically lays out nodes and edges using the dagre library for better readability.
 * - Highlights nodes and edges that are part of the execution path (with color and animation).
 * Data sources:
 * - Reads `langgraphJson` (graph structure) and `executionPath` (list of visited node IDs) from the chat context (`useChat`).
 * Usage:
 * - Place this component where you want to visualize the workflow graph for a chat.
 * - Requires `langgraphJson` and `executionPath` to be available in the chat context.
 */
import React, { useMemo } from "react";
import ReactFlow, { Background, Controls, MarkerType } from "reactflow";
import "reactflow/dist/style.css";
import { useChat } from "../../services/chatContext";
import dagre from 'dagre';

const getLayoutedElements = (nodes: any[], edges: any[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: direction });

  const nodeWidth = 172;
  const nodeHeight = 36;

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    };
    return node;
  });

  return { nodes, edges };
};


const LanggraphViz: React.FC = () => {
  const { langgraphJson, executionPath } = useChat();

  const layoutedElements = useMemo(() => {
    const safeExecutionPath = executionPath || [];
    const pathNodes = new Set(safeExecutionPath);
    const pathEdges = new Set<string>();
    for (let i = 0; i < safeExecutionPath.length - 1; i++) {
      pathEdges.add(`${safeExecutionPath[i]}-${safeExecutionPath[i + 1]}`);
    }
    const hasPath = safeExecutionPath.length > 0;

    const initialNodes = langgraphJson.nodes.map((n: any) => ({
      id: n.id,
      data: { label: n.data?.label || n.label },
      type: "default",
      style: {
        border: pathNodes.has(n.id) ? '2px solid #10B981' : '1px solid #9CA3AF',
        opacity: hasPath ? (pathNodes.has(n.id) ? 1 : 0.4) : 1,
        transition: 'all 0.3s ease',
        background: pathNodes.has(n.id) ? '#ddf4e4' : '#fff',
      },
    }));

  const initialEdges = langgraphJson.edges.map((e: any, i: number) => {
    let order = null;
    for (let j = 0; j < safeExecutionPath.length - 1; j++) {
      if (safeExecutionPath[j] === e.source && safeExecutionPath[j + 1] === e.target) {
        order = j + 1;
        break;
      }
    }
    const isInPath = order !== null;
    return {
      id: `e-${e.source}-${e.target}-${i}`,
      source: e.source,
      target: e.target,
      animated: isInPath,
      style: { stroke: isInPath ? '#10B981' : '#9CA3AF', strokeWidth: isInPath ? 2 : 1 },
      markerEnd: { type: MarkerType.ArrowClosed, color: isInPath ? '#10B981' : '#9CA3AF' },
      label: isInPath ? order?.toString() : undefined,
      labelStyle: { fill: '#10B981', fontWeight: 700 }
    };
  });

    return getLayoutedElements(initialNodes, initialEdges);
  }, [langgraphJson, executionPath]);

  if (!layoutedElements.nodes || layoutedElements.nodes.length === 0) {
    return null;
  }

  return (
    <div style={{ height: 500, width: "100%", border: '1px solid #e2e8f0', borderRadius: '8px', background: '#f8fafc' }}>
      <h3 style={{textAlign: 'center', margin: '10px 0', color: '#334155'}}>Vizualizace LangGraphu</h3>
      <ReactFlow
        nodes={layoutedElements.nodes}
        edges={layoutedElements.edges}
        fitView
      >
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
};

export default LanggraphViz;