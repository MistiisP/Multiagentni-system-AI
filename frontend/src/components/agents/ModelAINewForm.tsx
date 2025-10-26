/*
 * React component for creating a new AI model in the system.
 * Purpose:
 * - Allows users to add a new AI model by specifying its name, identifier, and API key.
 * Features:
 * - Uses react-hook-form for form state and validation.
 * - On submit, sends the new model data to the backend using the createModelAi function from the AI model context.
 * - Fetches the list of AI models on mount (to keep context up to date).
 * Usage:
 * - Place this component on a page where you want to allow users to add new AI models.
 * - Requires the AI model context provider to be available.
 * Props: none
 */
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import '../../css/Agent.css';
import { useAI_Model } from '../../services/ai_modelContext';

type NewModelAIFormData = {
  name: string; 
  model_identifier: string; 
  api_key: string; 
}

const ModelAINewForm: React.FC = () => {
  const { register, handleSubmit, formState: { errors }, reset } = useForm<NewModelAIFormData>();
  const { fetchAIModels, createModelAi } = useAI_Model();
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    fetchAIModels();
  }, [fetchAIModels]);


  const onSubmit = async (data: NewModelAIFormData) => {
    setFormError(null);
  
    const dataToSend: NewModelAIFormData = {
        name: data.name,
        model_identifier: data.model_identifier,
        api_key: data.api_key
    };

    try {
      await createModelAi(dataToSend);
      reset();
    } catch (error: any) {
      console.error('Chyba při vytváření nového AI modelu:', error);
    }
  };

  return (
    <div className="new-AImodel-container">
      <h2>Vytvoř nový AI model</h2>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="form-group">
          <input type="text" id="name" placeholder='Name' {...register('name', { required: 'Name is required' })} />
          {errors.name && <span className="error">{errors.name.message}</span>}
        </div>

        <div className="form-group">
          <textarea id="model_identifier" rows={5} placeholder='Identifier' {...register('model_identifier', { required: 'Identifier is required' })} />
          {errors.model_identifier && <span className="error">{errors.model_identifier.message}</span>}
        </div>

        <div className="form-group">
          <textarea id="api_key" rows={5} placeholder='Api key' {...register('api_key')} />
        </div>

        <button type="submit" className="new-agent-button">Create AI Model</button>
        {formError && <div className="error-message">{formError}</div>}

      </form>
    </div>
  );
};  

export default ModelAINewForm;
