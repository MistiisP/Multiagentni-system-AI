import React from 'react';
import { useChat } from '../../services/chatContext';
import '../../css/Chat.css';
import DeleteChatButton from './DeleteChatButton';
import RenameButton from './RenameButton';

const ListOfChats: React.FC = () => {
  const {chats, loadingChats, error, selectChat, activeChat} = useChat();

  const handleChatClick = (chatId: number) => {
    selectChat(chatId);
  };

  if (error) {
    return <div className="list-of-chats-status error">{error}</div>;
  }

  return (
    <div className="list-of-chats">
      {chats.length === 0 && !loadingChats && (
        <div className="chat-item-empty">Zatím nemáte žádné konverzace.</div>
      )}
      
      {chats.map(chat => (
        <div key={chat.id} className={`chat-item ${activeChat && chat.id === activeChat.id ?'active' : ''}`} onClick={() => handleChatClick(chat.id)}>
          <div className="chat-name">{chat.name}</div>
          <div className="chat-last-message">{chat.last_message}</div>
          <div className="timestamp-delete">
            <div className="chat-timestamp">{chat.timestamp}</div>
            <RenameButton chatID={chat.id} />
            <DeleteChatButton chatID={chat.id} />
          </div>
        </div>
      ))}
    </div>
  );
};

export default ListOfChats;