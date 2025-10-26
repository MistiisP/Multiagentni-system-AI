import React, { useState } from 'react';
import { useChat } from '../../services/chatContext';
import '../../css/Chat.css';

interface InputMessageProps {
  onSend: (message: string) => Promise<void>;
}

const InputMessage: React.FC<InputMessageProps> = ({ onSend }) => {
  const [message, setMessage] = useState('');
  const { isAiTyping } = useChat();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isAiTyping) return;

    await onSend(message);
    setMessage('');
  };

  return (
    <form className="input-message-wrapper" onSubmit={handleSubmit}>
      <div className="input-message">
        <i className='bx bx-plus'></i>
        <input type="text" placeholder="Zeptejte se" value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={isAiTyping}
        />
        <button type="submit"><i className='bx bx-up-arrow-alt'></i></button>
      </div>
    </form>
  );
};

export default InputMessage;