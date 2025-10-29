/*
 * React context for managing agent-related data and operations in the application.
 * Purpose:
 * - Centralizes all logic for fetching, creating, updating, and deleting agents, as well as assigning agents to chats.
 * - Provides state and functions for accessing all agents, agents assigned to a specific chat, and managing agent lifecycle.
 * Features:
 * - Fetches all agents or agents assigned to a specific chat from the backend.
 * - Allows creating, updating, and deleting agents.
 * - Supports assigning and removing agents from chats.
 * - Handles authentication (requires user token) and automatic logout on 401 errors.
 * - Manages loading and error states for all operations.
 * Usage:
 * - Wrap your application (or relevant part) with <AgentProvider>.
 * - Access agent data and functions in components using the useAgents() hook.
 * Provided context value:
 * - allAgents: List of all agents in the system.
 * - activeChatAgents: List of agents assigned to the currently selected chat.
 * - loading: Boolean indicating if an operation is in progress.
 * - error: Error message, if any.
 * - fetchAllAgents: Fetches all agents from the backend.
 * - fetchAgentsForChat: Fetches agents assigned to a specific chat.
 * - createAgent: Creates a new agent.
 * - addAgentToChat: Assigns an agent to a chat.
 * - removeAgentFromChat: Removes an agent from a chat.
 * - updateAgent: Updates an agent's data.
 * - deleteAgent: Deletes an agent.
 */
import React, { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { useAuth } from './authContext';


export interface ModelOfAI {
    id: number;
    name: string;
    model_identifier: string;
}

export interface Agent {
    id: number;
    description: string | null;
    name: string;
    prompt: string;
    models_ai: ModelOfAI[];
    tools: string[] | null;
    code: string | null;
}

export interface AgentCreateData {
    name: string;
    description: string | null;
    prompt: string;
    model_ids: number[];
    tools: string[] | null;
    code: string | null;
}


export type AgentUpdateData = Partial<AgentCreateData>;


interface AgentContextType {
    allAgents: Agent[];
    activeChatAgents: Agent[];
    loading: boolean;
    error: string | null;
    fetchAllAgents: () => Promise<void>;
    fetchAgentsForChat: (chatId: number) => Promise<void>;
    createAgent: (agentData: AgentCreateData) => Promise<void>;
    addAgentToChat: (chatId: number, agentId: number) => Promise<void>;
    removeAgentFromChat: (chatId: number, agentId: number) => Promise<void>;
    updateAgent: (agentId: number, data: AgentUpdateData) => Promise<void>;
    deleteAgent: (agentId: number) => Promise<void>;
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

export const AgentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const { token, logout } = useAuth();

    const [allAgents, setAllAgents] = useState<Agent[]>([]);
    const [activeChatAgents, setActiveChatAgents] = useState<Agent[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);


    const handleApiResponse = useCallback((response: Response) => {
        if (response.status === 401) {
            if (logout) logout();
            throw new Error("Platnost přihlášení vypršela.");
        }
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.detail || `Chyba sítě: ${response.statusText}`);
            }).catch(() => {
                throw new Error(`Chyba sítě: ${response.statusText}`);
            });
        }
        return response;
    }, [logout]);



    const fetchAllAgents = useCallback(async () => {
        if (!token) return;
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/agents/', { headers: { 'Authorization': `Bearer ${token}` } });
            handleApiResponse(response);
            const data: Agent[] = await response.json();
            setAllAgents(data);
        } catch (err: any) { setError(err.message); } 
        finally { setLoading(false); }
    }, [token, handleApiResponse]);



    const fetchAgentsForChat = useCallback(async (chatId: number) => {
        if (!token || !chatId) return;
        setLoading(true);
        try {
            const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}/agents`, { headers: { 'Authorization': `Bearer ${token}` } });
            handleApiResponse(response);
            const data: Agent[] = await response.json();
            setActiveChatAgents(data);
        } catch (err: any) { 
            setError(err.message); 
            setActiveChatAgents([]);
        } 
        finally { 
            setLoading(false); 
        }
    }, [token, handleApiResponse]);



    const createAgent = async (agentData: AgentCreateData) => {
        if (!token) throw new Error("Not authenticated");
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/agents/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(agentData)
            });
            handleApiResponse(response);
            await fetchAllAgents(); 
        } catch (err:any) {
            setError(err.mesage);
            throw err;
        } 
        finally {
            setLoading(false);
        }
    };






    const addAgentToChat = useCallback(async (chatId: number, agentId: number) => {
        if (!token || !chatId || !agentId) return;
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}/agents/${agentId}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            handleApiResponse(response);
            await fetchAgentsForChat(chatId);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [token, handleApiResponse, fetchAgentsForChat]);


    const removeAgentFromChat = useCallback(async (chatId: number, agentId: number) => {
        if (!token || !chatId || !agentId) return;
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`http://127.0.0.1:8000/chats/${chatId}/agents/${agentId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            handleApiResponse(response);
            await fetchAgentsForChat(chatId);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [token, handleApiResponse, fetchAgentsForChat]);


    const updateAgent = async (agentId: number, data: AgentUpdateData) => {
        if (!token) throw new Error("Not authenticated");
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`http://127.0.0.1:8000/agents/${agentId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                body: JSON.stringify(data),
            });
            handleApiResponse(response);
            await fetchAllAgents();
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const deleteAgent = async (agentId: number) => {
        if (!token) throw new Error("Not authenticated");
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`http://127.0.0.1:8000/agents/${agentId}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` },
            });
            handleApiResponse(response);
            await fetchAllAgents();
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const value = {allAgents, activeChatAgents, loading, error, fetchAllAgents, fetchAgentsForChat, createAgent, addAgentToChat, removeAgentFromChat, deleteAgent, updateAgent};
    return <AgentContext.Provider value={value}>{children}</AgentContext.Provider>;
};

export const useAgents = () => {
    const context = useContext(AgentContext);
    if (context === undefined) {
        throw new Error('useAgents must be used within an AgentProvider');
    }
    return context;
};