import React from 'react';
import '../../css/Chat.css';
import InputMessage from './InputMessage';
import Messages from './Messages';
import AnswerMessage from './AnswerMessage';
import ChatAgentsSetting from '../agents/ChatAgentsSetting';
import LanggraphViz from '../agents/LanggraphVis';
import { useChat } from "../../services/chatContext";
import { useGraph } from "../../services/graphContext";


interface FormattedMessage {
    id: string;
    text: string;
    sender: 'user' | 'ai';
}

const ChatCard: React.FC = () => {
    const {activeChat, messages, loadingMessages, isAiTyping, error, handleAiAnswer, sendMessage, aiAnswer} = useChat();
    const {graphId} = useGraph();

    const formattedMessages: FormattedMessage[] = messages.map(msg => ({
        id: msg.id.toString(),
        text: msg.content,
        sender: msg.sender_id !== null ? 'user' : 'ai'
    }));

    const handleSendMessageInActiveChat = async (message: string) => {
        await sendMessage(message);
        await handleAiAnswer([message], graphId ?? activeChat?.graph_id ?? undefined);
    };


    return (
        <div className="chat-card-container"> 
            <div className="chat-card">
                <div className="chat-messages">
                    {loadingMessages && <p>Načítám zprávy...</p>}
                    {error && <p style={{ color: 'red' }}>{error}</p>}
                    {!loadingMessages && !error && <Messages messages={formattedMessages} />}
                    {isAiTyping && (
                        <div className="thinking">
                            <AnswerMessage text={aiAnswer} />
                        </div>
                    )}   
                    {aiAnswer && !isAiTyping && (
                        <div className="chat-answer">
                            <AnswerMessage text={aiAnswer} />
                            <LanggraphViz />
                        </div>
                    )}
                </div>
                
                <div className="chat-input">
                    <InputMessage onSend={handleSendMessageInActiveChat}/>
                </div>
            </div>
            {activeChat && (
                <ChatAgentsSetting activeChatId={activeChat.id} activeGraphId={activeChat.graph_id}/>
            )}
        </div>
    );
};

export default ChatCard;