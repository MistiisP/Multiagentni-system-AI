/**
 * React component for displaying a list of agents assigned to a specific chat.
 * Purpose:
 * - This component is intended for the chat settings page, where it shows all agents assigned to the given chat.
 * Features:
 * - Fetches and displays agents associated with the provided chatId.
 * - Shows agent name, prompt, and AI model for each agent.
 * - Informs the user if no agents are assigned to the chat.
 * Props:
 * - chatId (number): The ID of the chat for which to display assigned agents.
 */
import React, { useEffect } from 'react';
import { useAgents } from '../../services/agentContext';
import '../../css/Agent.css'; 

interface DetailsInfoAgentProps {
  chatId: number;
}

const DetailsInfoAgent: React.FC<DetailsInfoAgentProps> = ({ chatId }) => {
  const { activeChatAgents, loading, error, fetchAgentsForChat } = useAgents();

  useEffect(() => {
    if (chatId) {
      fetchAgentsForChat(chatId);
    }
  }, [chatId, fetchAgentsForChat]);

  if (loading) {
    return <div className="agents-item-empty">Načítám agenty chatu...</div>;
  }

  if (error) {
    return <div className="agents-item-empty error">Chyba: {error}</div>;
  }

  if (activeChatAgents.length === 0) {
    return <div className="agents-item-empty">Tento chat nemá přiřazené žádné agenty.</div>;
  }

  return (
    <div className="list-of-agents-details-info">
      <h4>Agenti v tomto chatu</h4>
      <ul className="chat-agents-list">
        {activeChatAgents.map(agent => (
          <li key={agent.id} className="chat-agent-item">
            <div className="agent-info">
              <strong className="chat-agent-name">{agent.name}</strong>
              <p className="agent-prompt"><strong>Prompt: </strong>{agent.prompt}</p>
              <p className="agent-model"><strong>Model: </strong>{agent.models_ai && agent.models_ai.length > 0 ? agent.models_ai.map((m: any) => m.name).join(", ") : "Žádné modely"}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DetailsInfoAgent;