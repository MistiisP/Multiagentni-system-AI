/*
 * React component for managing agents assigned to a specific chat.
 * Purpose:
 * - This component is intended for the chat settings page, allowing users to add or remove agents assigned to a given chat.
 * Features:
 * - Fetches all available agents on mount.
 * - Allows the user to select an agent from a dropdown list.
 * - Provides buttons to add the selected agent to the chat or remove them from the chat.
 * Props:
 * - chatId (number): The ID of the chat for which agents are being managed.
 */
import React, { useState, useEffect } from 'react';
import { useAgents } from '../../services/agentContext';
import '../../css/Agent.css';

interface ChatManageAgentsProps {
  chatId: number;
}

const ChatManageAgents: React.FC<ChatManageAgentsProps> = ({ chatId }) => {
  const { allAgents, fetchAllAgents, addAgentToChat, removeAgentFromChat, error } = useAgents();
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');

  useEffect(() => {
    fetchAllAgents();
  }, [fetchAllAgents]);

  const handleAdd = () => {
    if (!selectedAgentId) {
      alert('Prosím, vyberte agenta.');
      return;
    }
    addAgentToChat(chatId, Number(selectedAgentId));
  };

  const handleRemove = () => {
    if (!selectedAgentId) {
      alert('Prosím, vyberte agenta.');
      return;
    }
    removeAgentFromChat(chatId, Number(selectedAgentId));
  };

  return (
    <div className="manage-agents-container">
      <h4>Spravovat agenty</h4>
      <div className="manage-agents-controls">
        <select className="agent-select"
          value={selectedAgentId}
          onChange={(e) => setSelectedAgentId(e.target.value)} >
          <option value="">Vyberte agenta</option>
          {allAgents.map(agent => (
            <option key={agent.id} value={agent.id}>
              {agent.name}
            </option>
          ))}
        </select>
        <button id="btn-add" onClick={handleAdd} className="bx bxs-plus-circle"></button>
        <button id="btn-delete" onClick={handleRemove} className="bx bxs-trash"></button>
      </div>
      {error && <p className="error-message small">{error}</p>}
    </div>
  );
}; 
                        
export default ChatManageAgents;