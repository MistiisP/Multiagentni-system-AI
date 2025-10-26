import React, { useEffect, useRef } from "react";
import "../../css/Chat.css";

type Message = {
  id: string;
  sender: "user" | "ai";
  text: string;
};

const Messages: React.FC<{ messages: Message[] }> = ({ messages }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!bottomRef.current) return;
    bottomRef.current.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div ref={containerRef} className="messages">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`message ${
            message.sender === "user" ? "user-message" : "ai-message"
          }`}
        >
          {message.text}
        </div>
      ))}

      <div ref={bottomRef} style={{ height: "1px" }}></div>
    </div>
  );
};

export default Messages;
