/* 
 * React context for managing AI model data and operations in the application.
 * Purpose:
 * - Centralizes all logic for fetching, creating, updating, and deleting AI models.
 * - Provides state and functions for accessing all AI models and managing their lifecycle.
 * Features:
 * - Fetches all AI models from the backend.
 * - Allows creating, updating, and deleting AI models.
 * - Handles authentication (requires user token) and automatic logout on 401 errors.
 * - Manages loading and error states for all operations.
 * Usage:
 * - Wrap your application (or relevant part) with <AI_ModelProvider>.
 * - Access AI model data and functions in components using the useAI_Model() hook.
 * Provided context value:
 * - aiModels: List of all AI models in the system.
 * - loading: Boolean indicating if an operation is in progress.
 * - error: Error message, if any.
 * - fetchAIModels: Fetches all AI models from the backend.
 * - createModelAi: Creates a new AI model.
 * - updateAiModel: Updates an existing AI model.
 * - deleteAiModel: Deletes an AI model.
 */
import React, { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { useAuth } from './authContext';

export interface AIModel {
    id: number;
    name: string;
    model_identifier: string;
}

interface AIModelCreate {
    name: string;
    model_identifier: string;
    api_key: string;
}


interface AI_ModelContextType {
    aiModels: AIModel[];
    loading: boolean;
    error: string | null;
    fetchAIModels: () => Promise<void>;
    createModelAi: (data: AIModelCreate) => Promise<void>;
    updateAiModel: (modelId: number, data: AIModelCreate) => Promise<void>;
    deleteAiModel: (modelId: number) => Promise<void>;
}

const AI_ModelContext = createContext<AI_ModelContextType | undefined>(undefined);

export const AI_ModelProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [aiModels, setAIModels] = useState<AIModel[]>([]);
    const { token, logout } = useAuth();
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);


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


    const fetchAIModels = useCallback(async () => {
        if (!token) return;
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/ai_models/', { 
                headers: { 'Authorization': `Bearer ${token}` } }
            );
            handleApiResponse(response);
            const data: AIModel[] = await response.json();
            setAIModels(data);
        } catch (err: any) { setError(err.message); } 
        finally { setLoading(false); }
    }, [token, handleApiResponse]);



    
    const createModelAi = async (aiModelData: AIModelCreate) => {
        if (!token) throw new Error("Not authenticated");
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/ai_models/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(aiModelData)
            });
            handleApiResponse(response);
            await fetchAIModels(); 
        } catch (err:any) {
            setError(err.mesage);
            throw err;
        } 
        finally {
            setLoading(false);
        }
    };

        
    const updateAiModel = async (modelId: number, data: AIModelCreate) => {
        if (!token) throw new Error("Not authenticated");
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`http://127.0.0.1:8000/ai_models/${modelId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                body: JSON.stringify(data),
            });
            handleApiResponse(response);
            await fetchAIModels();
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const deleteAiModel = async (modelId: number) => {
        if (!token) throw new Error("Not authenticated");
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`http://127.0.0.1:8000/ai_models/${modelId}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` },
            });
            handleApiResponse(response);
            await fetchAIModels();
        } catch (err: any) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };
        

    const value = { aiModels, loading, error, fetchAIModels, createModelAi, updateAiModel, deleteAiModel };
    return <AI_ModelContext.Provider value={value}>{children}</AI_ModelContext.Provider>;
};

export const useAI_Model = () => {
    const context = useContext(AI_ModelContext);
    if (context === undefined) {
        throw new Error('useAI_Model must be used within an AgentProvider');
    }
    return context;
};