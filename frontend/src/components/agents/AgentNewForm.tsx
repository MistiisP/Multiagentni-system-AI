/*
 * React component for creating a new agent in the system.
 * Features:
 * - Allows the user to enter name, description, prompt, optional code, select an AI model, and choose tools.
 * - Loads available AI models (from useAI_Model context) and tools (from useTools context).
 * - Sends data to the backend using the createAgent function from agentContext.
 * - Displays validation errors and possible submission errors.
 * Usage:
 *  - Place this component on the page where you want to allow agent creation.
 *  - Must be wrapped in context providers (AgentsProvider, AI_ModelProvider, ToolsProvider).
 * Props: none
 */
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useAgents, type AgentCreateData } from '../../services/agentContext';
import { useAI_Model } from '../../services/ai_modelContext';
import { useTools } from '../../services/toolsContext';
import '../../css/Agent.css';

type NewAgentFormData = {
  name: string; 
  description?: string;
  prompt: string; 
  model_ai_id: string; 
  tools?: string[];
  code?: string; 
}


const AgentNewForm: React.FC = () => {
  const { register, handleSubmit, formState: { errors }, reset } = useForm<NewAgentFormData>();
  const { createAgent} = useAgents();
  const { aiModels, fetchAIModels } = useAI_Model();
  const [formError, setFormError] = useState<string | null>(null);
  const { tools } = useTools();


  useEffect(() => {
    fetchAIModels();
  }, [fetchAIModels]);


  const onSubmit = async (data: NewAgentFormData) => {
    setFormError(null);
  
    let selectedTools: string[] = [];
    if (Array.isArray(data.tools)) {
      selectedTools = data.tools;
    } else if (typeof data.tools === "string") {
      selectedTools = [data.tools];
    }

    const dataToSend: AgentCreateData = {
        name: data.name,
        description: data.description || null,
        prompt: data.prompt,
        model_ai_id: Number(data.model_ai_id),
        tools: selectedTools || [],
        code: data.code || null,
    };

    if (isNaN(dataToSend.model_ai_id)) {
        setFormError("Prosím, vyberte platný AI model.");
        return;
    }

    try {
      await createAgent(dataToSend);
      reset();
    } catch (error: any) {
      console.error('Chyba při vytváření agenta:', error);
    }
  };

  return (
    <div className="new-agent-container">
      <h2>Vytvoř nového agenta</h2>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="form-group">
          <input type="text" id="name" placeholder='Name' {...register('name', { required: 'Name is required' })} />
          {errors.name && <span className="error">{errors.name.message}</span>}
        </div>
        <div className="form-group">
          <textarea id="description" rows={2} placeholder='Description (optional)' {...register('description')} />
        </div>
        <div className="form-group">
          <textarea id="prompt" rows={5} placeholder='Prompt' {...register('prompt', { required: 'Prompt is required' })} />
          {errors.prompt && <span className="error">{errors.prompt.message}</span>}
        </div>
        <div className="form-group">
          <select id="model_ai_id" {...register('model_ai_id', { required: 'AI Model is required' })}>
            <option value="">Vyber AI model</option>
            {aiModels.map(model => ( <option key={model.id} value={model.id}>{model.name}</option> ))}
          </select>
          {errors.model_ai_id && <span className="error">{errors.model_ai_id.message}</span>}
        </div>
        <div className="form-group">
          <label>Nástroje (tools):</label>
            {tools.length === 0 && <div>Žádné nástroje nejsou dostupné.</div>}
          {tools.map(tool => (
            <label key={tool.name} style={{ marginRight: 10 }}>
              <input type="checkbox" value={tool.name} {...register("tools")}/>
              {tool.name}{tool.description ? ` – ${tool.description}` : ""}
            </label>))
          }
        </div>
        <div className="form-group">
          <textarea id="code" rows={5} placeholder='Code (optional)' {...register('code')}/>
        </div>
        <button type="submit" className="new-agent-button">Create Agent</button>
        {formError && <div className="error-message">{formError}</div>}
      </form>
    </div>
  );
};

export default AgentNewForm;


