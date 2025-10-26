/*
 * React context for managing available tools in the application.
 * Purpose:
 * - Centralizes logic for fetching and providing the list of available tools to any component in the app.
 * Features:
 * - Fetches the list of tools from the backend on mount.
 * - Provides a function to reload tools on demand.
 * - Manages loading state during fetch operations.
 * Usage:
 * - Wrap your application (or relevant part) with <ToolsProvider>.
 * - Access tools and related functions in components using the useTools() hook.
 * Provided context value:
 * - tools: Array of available tools (with name and optional description).
 * - isLoading: Boolean indicating if the tools are being loaded.
 * - reloadTools: Function to reload the list of tools from the backend.
 */
import React, { createContext, useContext, useEffect, useState } from "react";

export type Tool = {
  name: string;
  description?: string;
};

interface ToolsContextType {
  tools: Tool[];
  isLoading: boolean;
  reloadTools: () => void;
}

const ToolsContext = createContext<ToolsContextType | undefined>(undefined);

export const ToolsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchTools = () => {
    setIsLoading(true);
    fetch("http://127.0.0.1:8000/tools")
      .then((res) => res.json())
      .then(setTools)
      .catch(() => setTools([]))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchTools();
  }, []);

  return (
    <ToolsContext.Provider value={{ tools, isLoading, reloadTools: fetchTools }}>
      {children}
    </ToolsContext.Provider>
  );
};

export const useTools = () => {
  const context = useContext(ToolsContext);
  if (!context) {
    throw new Error("useTools must be used within a ToolsProvider");
  }
  return context;
};