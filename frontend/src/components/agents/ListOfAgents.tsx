/*
 * React component for displaying and managing the list of all agents in the system.
 * Purpose:
 * - Shows all agents available to the user, including their details and assigned tools.
 * - Allows editing and deleting agents directly from the list.
 * Features:
 * - Fetches all agents on mount using the agent context.
 * - Displays agent details: name, description, prompt, AI model, tools, and code.
 * - Provides edit and delete buttons for each agent.
 * - Edit action opens a series of prompts to update agent properties (name, description, prompt, model, tools, code).
 * Usage:
 * - Place this component on a page where you want to manage agents.
 * - Requires context providers for agents, AI models, and tools to be available.
 * Props: none
 */
import React, { useEffect } from 'react';
import { useAgents } from '../../services/agentContext';
import { useAI_Model } from '../../services/ai_modelContext';
import { useTools } from '../../services/toolsContext';
import '../../css/Agent.css';

const ListOfAgents: React.FC = () => {
    const { allAgents, loading, fetchAllAgents, updateAgent, deleteAgent } = useAgents();
    const { aiModels } = useAI_Model();
    const { tools } = useTools();

    useEffect(() => {
        fetchAllAgents();
    }, [fetchAllAgents]);

    if (allAgents.length === 0 && !loading) {
        return <div className="agents-item-empty">Zatím nemáte žádné agenty</div>
    }


  const handleEdit = (agent: any) => {
    const safeValue = (val: any) => (val === null || val === undefined ? "" : val);

    const name = window.prompt("Zadejte nové jméno agenta:", safeValue(agent.name));
    if (name === null) return;

    const description = window.prompt("Zadejte nový popis agenta:", safeValue(agent.description));
    if (description === null) return;

    const prompt = window.prompt("Zadejte nový prompt:", safeValue(agent.prompt));
    if (prompt === null) return;

    const modelList = aiModels.map(m => `${m.id}: ${m.name}`).join('\n');
    const model_ai_id_str = window.prompt(
      `Zadejte nové ID modelu:\n${modelList}`,
      safeValue(agent.model_ai_id?.toString())
    );
    if (model_ai_id_str === null) return;

    const toolsList = tools.map(tool => `${tool.name}`).join('\n');
    const tools_str = window.prompt(
      `Zadejte nové nástroje (oddělené čárkami):\n${toolsList}`,
      (agent.tools ?? []).join(", ")
    );
    if (tools_str === null) return;

    const code = window.prompt("Zadejte nový kód:", safeValue(agent.code));
    if (code === null) return;

    const updateData: any = {};

    if (name.trim() && name !== agent.name) updateData.name = name.trim();
    if (description.trim() && description !== agent.description) updateData.description = description.trim();
    if (prompt.trim() && prompt !== agent.prompt) updateData.prompt = prompt.trim();

  
    if (model_ai_id_str.trim() !== "") {
      const modelIdNum = Number(model_ai_id_str);
      if (!isNaN(modelIdNum) && modelIdNum > 0 && modelIdNum !== agent.model_ai_id) {
        updateData.model_ai_id = modelIdNum;
      }
    }

    if (tools_str.trim() && tools_str !== (agent.tools ?? []).join(", ")) {
      updateData.tools = tools_str.split(",").map(t => t.trim()).filter(Boolean);
    }

    if (code.trim() && code !== agent.code) updateData.code = code.trim();

    if (Object.keys(updateData).length > 0) {
      updateAgent(agent.id, updateData);
    } else {
      console.log("Žádné změny nebyly provedeny.");
    }
  };



    return (
      <div className="list-of-agents">
        <h2><i className='bx bxs-mask'></i> Seznam agentů</h2>
          <ul className="agents-list">
              {allAgents.map(agent => (
                <li key={agent.id} className="agent-item">
                    <div className="agent-info">
                        <strong className="agent-name">{agent.name}</strong>
                        <p className="agent-description"><strong>Stručný popis: </strong>{agent.description}</p>
                        <p className="agent-prompt"><strong>Prompt: </strong>{agent.prompt}</p>
                        <p className="agent-model"><strong>Model: </strong>{agent.model_ai_name}</p>
                        <p className="agent-tools"><strong>Nástroje: </strong>{Array.isArray(agent.tools)? agent.tools.join(", "): agent.tools}</p>
                        <p className="agent-code"><strong>Kód: </strong>{agent.code}</p>
                    </div>
                    <div className="agent-actions">
                        <button id="btn-edit" onClick={() =>  handleEdit(agent)}><i className='bx bxs-pencil'></i> </button>
                        <button id="btn-delete"  onClick={() => deleteAgent(agent.id)}><i className='bx bxs-trash'></i> </button>
                    </div>
                </li>
              ))}
          </ul>
      </div>
    )
}

export default ListOfAgents;