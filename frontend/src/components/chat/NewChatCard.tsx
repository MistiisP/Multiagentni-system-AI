import React from 'react';
import '../../css/Chat.css';
import InputMessage from './InputMessage';
import { useChat } from '../../services/chatContext';

const NewChatCard: React.FC = () => {
  const { createNewChat } = useChat();

  const handleCreateChat = async (message: string) => {
    await createNewChat(message);
  };

  return (
    <div className="new-chat-content">
      <div className="new-chat-bg">
        <div className="new-chat-tittle">
          <h2>Máte otázku?</h2>
          <p>Vaše první zpráva bude použita jako název konverzace.</p>
        </div>
        <InputMessage onSend={handleCreateChat} />
      </div>
    </div>
  );
};

export default NewChatCard;