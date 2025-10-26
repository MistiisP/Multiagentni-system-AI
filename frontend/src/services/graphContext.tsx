/*
 * React context for managing the workflow graph ID and loading state associated with a chat.
 * Purpose:
 * - Centralizes logic for tracking and updating the current workflow graph ID based on the active chat.
 * - Provides state and functions for accessing and updating the graph ID and loading status.
 * Features:
 * - Fetches the graph ID associated with a given chat ID from the backend.
 * - Updates the graph ID automatically when the active chat changes.
 * - Manages loading state during fetch operations.
 * Usage:
 * - Wrap your application (or relevant part) with <GraphProvider>.
 * - Access graph state and functions in components using the useGraph() hook.
 * Provided context value:
 * - graphId: The current workflow graph ID (or null if none).
 * - setGraphId: Function to manually set the graph ID.
 * - isLoading: Boolean indicating if the graph ID is being loaded.
 * - setActiveChatId: Function to set the active chat ID (triggers graph ID fetch).
 */
import React, { createContext, useContext, useState, useEffect } from "react";
import {useAuth} from "./authContext";

interface GraphContextType {
  graphId: number | null;
  setGraphId: (id: number | null) => void;
  isLoading: boolean;
  setActiveChatId: (id: number) => void;
}

const GraphContext = createContext<GraphContextType | undefined>(undefined);

export const GraphProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [graphId, setGraphId] = useState<number | null>(null);
  const [activeChatId, setActiveChatId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const {token} = useAuth();

  useEffect(() => {
    if (activeChatId == null) {
      setGraphId(null);
      return;
    }
    setIsLoading(true);
    fetch(`http://127.0.0.1:8000/chats/${activeChatId}`, {
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(chat => {
        setGraphId(chat.graph_id ? Number(chat.graph_id) : null);
      })
      .catch(() => setGraphId(null))
      .finally(() => setIsLoading(false));
  }, [activeChatId]);

  return (
    <GraphContext.Provider value={{ graphId, setGraphId, isLoading, setActiveChatId }}>
      {children}
    </GraphContext.Provider>
  );
};

export const useGraph = () => {
  const context = useContext(GraphContext);
  if (!context) throw new Error("useGraph must be used within a GraphProvider");
  return context;
};