/*
 * React context for managing chat-related data and operations in the application.
 * Purpose:
 * - Centralizes all logic for fetching, creating, updating, and deleting chats and chat messages.
 * - Provides state and functions for accessing chat previews, messages, active chat, and AI interactions.
 * Features:
 * - Fetches all chats and messages for the authenticated user.
 * - Allows creating new chats, sending messages, deleting and renaming chats.
 * - Manages the currently active chat and synchronizes it with the URL.
 * - Handles AI responses via WebSocket, including streaming multi-agent system outputs, execution path, and graph structure.
 * - Manages loading and error states for all operations.
 * Usage:
 * - Wrap your application (or relevant part) with <ChatProvider>.
 * - Access chat state and functions in components using the useChat() hook.
 * Provided context value:
 * - chats: List of chat previews for the user.
 * - messages: List of messages for the active chat.
 * - activeChat: The currently selected chat.
 * - loadingChats: Boolean indicating if chats are being loaded.
 * - loadingMessages: Boolean indicating if messages are being loaded.
 * - isAiTyping: Boolean indicating if the AI is currently generating a response.
 * - error: Error message, if any.
 * - selectChat: Function to select a chat by ID.
 * - sendMessage: Function to send a message to the active chat.
 * - createNewChat: Function to create a new chat.
 * - fetchChats: Function to fetch all chats.
 * - deleteChat: Function to delete a chat.
 * - renameName: Function to rename a chat.
 * - handleAiAnswer: Function to handle AI answer via WebSocket (multi-agent system).
 * - aiAnswer: The latest AI answer for the active chat.
 * - langgraphJson: The workflow graph structure for the current chat (if available).
 * - executionPath: The list of nodes visited during the last workflow execution.
 */
import React, {useState, useEffect, useContext, createContext, type ReactNode, useCallback} from 'react';
import {useAuth} from "./authContext";
import { useNavigate, useLocation } from 'react-router-dom';

export interface ChatPreview {
    id: number
    name: string;
    last_message: string;
    timestamp: string;
    graph_id: number | null;
}

export interface Message {
    id: number
    content: string
    sender_id: number | null //if null then sender is AI
    timestamp: string
}

interface ChatContextType {
  chats: ChatPreview[];
  messages: Message[];
  activeChat: ChatPreview | null;
  loadingChats: boolean;
  loadingMessages: boolean;
  isAiTyping: boolean;
  error: string | null;
  selectChat: (chatID: number | null) => void;
  sendMessage: (content: string) => Promise<void>;
  createNewChat: (content: string) => Promise<number | undefined>;
  fetchChats: () => void;
  deleteChat: (chatID: number) => Promise<void>;
  renameName: (content: string, chatID: number) => Promise<void>
  handleAiAnswer: (userMessage: string[], graphId?: number) => Promise<void>;
  aiAnswer: string;
  langgraphJson: any;
  executionPath: string[];
}


const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{children: ReactNode}> = ({children}) => {
    const {token, logout, loading: authLoading} = useAuth();
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();
    const location = useLocation();

    //list of chats
    const [chats, setChats] = useState<ChatPreview[]>([]);
    const [loadingChats, setLoadingChats] = useState<boolean>(true);
    //chat card and messages
    const [isAiTyping, setIsAiTyping] = useState<boolean>(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [loadingMessages, setLoadingMessages] = useState<boolean>(false);
    const [activeChat, setActiveChat] = useState<ChatPreview | null>(null);


    
    const handleApiResponse = useCallback((response: Response) => {
        if (response.status === 401) {
            if (logout) logout();
            throw new Error("Platnost přihlášení vypršela. Přihlaste se prosím znovu.");
        }
        if (!response.ok) {
            throw new Error(`Chyba sítě: ${response.statusText}`);
        }
    }, [logout]);
    

    const fetchChats = useCallback(async () => {
        if (!token) return;
        setLoadingChats(true);
        setError(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/chats/', {
            headers: { 'Authorization': `Bearer ${token}` }
            });
            handleApiResponse(response);
            const data: ChatPreview[] = await response.json();

            setChats(data);
        }
        catch (err: any) { setError(err.message); } 
        finally { setLoadingChats(false); }  
    }, [token]);


    const fetchMessages = useCallback(async (chatID: number) => {
        if (!token) return;
        setLoadingMessages(true);
        setError(null);
        try {
            const response = await fetch(`http://127.0.0.1:8000/chats/${chatID}/messages`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            handleApiResponse(response);
            const data: Message[] = await response.json();
            setMessages(data);
        } catch (err: any) { setError(err.message); } 
          finally { setLoadingMessages(false);
        }
    }, [token]);



    const createNewChat = async (content: string): Promise<number | undefined> => {
        if (!token) return;
        setError('');
        try {
            const response = await fetch('http://127.0.0.1:8000/chats/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ content }),
            });

            handleApiResponse(response);
            const newChat: ChatPreview = await response.json();
            
            await fetchChats(); 
            setActiveChat(newChat);
            
            return newChat.id; 
        } catch (error: any) {
            setError(error.message || 'Neznámá chyba při vytvoření chatu.');
            return undefined;
        }
    };


    const sendMessage = async (content: string) => {
        if (!token || !activeChat) return;
        setError('');
        setIsAiTyping(true);

        try {
            const response = await fetch(`http://127.0.0.1:8000/chats/${activeChat.id}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`, },
            body: JSON.stringify({content}),
            });
            
            handleApiResponse(response);
            
            await fetchMessages(activeChat.id);
            await fetchChats();
        }
        catch (error: any) {
            setError(error.message || 'neznama chyba při odesílání');
        } finally {
            setIsAiTyping(false);
        }
    };


    const deleteChat = async (chatID: number) => {
        if (!token) return;
        setError(null);
        try {
            const response = await fetch(`http://127.0.0.1:8000/chats/${chatID}`, {
                method: 'DELETE',
                headers: {'Authorization': `Bearer ${token}`,}
            });
        
            handleApiResponse(response);
            await fetchChats();
        } catch (error:any) {
            setError(error.message || "neznáma chyba");
        }
    }

    const renameName =  async (content: string, chatID: number) => {
        if (!token) return;
        setError(null);
        try {
            const response = await fetch (`http://127.0.0.1:8000/chats/${chatID}/rename`, {
                method: "PATCH",
                headers: {'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json',},
                body: JSON.stringify({name: content}),
            });
            handleApiResponse(response);
            await fetchChats();
        } catch(error:any){
            setError(error.mesage || "neznáma chyba");
        }   
    }



    const [langgraphJson, setLanggraphJson] = useState<string | null>(null);
    const [executionPath, setExecutionPath] = useState<string[]>([]); 
    const [aiAnswer, setAiAnswer] = useState<string>("");



    const handleAiAnswer = async (userMessage: string[], graphId?: number) => {
        if (!graphId || !activeChat) {
            setAiAnswer('Nejprve vytvořte graf k novému chatu a poté znovu napište otázku.');
            return;
        }
        setAiAnswer('🧠 Multiagentní systém analyzuje váš požadavek');
        setIsAiTyping(true);

        setLanggraphJson(null);
        setExecutionPath(['__start__']);

        const ws = new WebSocket(`ws://127.0.0.1:8000/ws/run-graph/${graphId}?chat_id=${activeChat.id}`);
        ws.onopen = () => {
            console.log("WebSocket spojení navázáno.");
            ws.send(JSON.stringify({ input_messages: userMessage }));
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);

            switch (message.type) {
                case 'graph_json':
                    console.log("GRAPH_JSON:", message.data);
                    setLanggraphJson(message.data);
                    break;
                
                case 'node_output':
                    if (message.data) {
                        setAiAnswer(prev => prev + `**Výstup z agenta "${message.node}":**\n\n${message.data}\n\n---\n\n`);
                    }
                    
                    setExecutionPath(prevPath => {
                        if (!prevPath.includes(message.node)) {
                            return [...prevPath, message.node];
                        }
                        return prevPath;
                    });
                    break;

                case 'stream_end':
                    setIsAiTyping(false);
                    setExecutionPath(message.path || []);
                    if (message.final_answer) {
                        setAiAnswer(message.final_answer);
                    }
                    
                    fetchChats();
                    break;

                case 'error':
                    console.error("Chyba na WebSocketu:", message.data);
                    setAiAnswer(prev => prev + `\n**CHYBA:** ${message.data}`);
                    setIsAiTyping(false);
                    break;
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket chyba:", error);
            setAiAnswer('Došlo k chybě ve spojení.');
            setIsAiTyping(false);
        };

        ws.onclose = () => {
            console.log("WebSocket spojení uzavřeno.");
            setIsAiTyping(false);
        };
    };





    useEffect(() => {
        if (!authLoading && token) {
            fetchChats();
        }
    }, [authLoading, token, fetchChats]);


    useEffect(() => {
        if (activeChat) {
            fetchMessages(activeChat.id);
        }
    }, [activeChat]);



    useEffect(() => {
        if (location.pathname !== '/dashboard') {
            return;
        }
        if (activeChat) {
            if (location.search !== `?chatId=${activeChat.id}`) {
                navigate(`/dashboard?chatId=${activeChat.id}`, { replace: true });
            }
        } else {
            if (location.search.includes('chatId')) {
                navigate("/dashboard", { replace: true });
            }
        }
    }, [activeChat, navigate, location]);


    const selectChat = (chatID: number | null) => {
        if (chatID === null) {
            setActiveChat(null);
            setMessages([]);
            return;
        }
        const chatToSelect = chats.find(chat => chat.id === chatID);
        if (chatToSelect) {
            setActiveChat(chatToSelect);
        }
    };


    const value = {chats, messages, activeChat, loadingChats, loadingMessages, isAiTyping, error, selectChat, sendMessage, createNewChat, fetchChats, deleteChat, renameName, handleAiAnswer, aiAnswer, setAiAnswer, langgraphJson,  executionPath};
    return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = () => {
    const context = useContext(ChatContext);
    if (context === undefined) {
        throw new Error('useChat must be used within ChatProvider')
    }
    return context;
};
