import React from 'react';
import '../../css/Chat.css';

interface AnswerMessageProps {
  text: string;
}

const AnswerMessage: React.FC<AnswerMessageProps> = ({ text }) => {
  return (
    <div className="answer-message">
      {text}
    </div>
  );
};

export default AnswerMessage;