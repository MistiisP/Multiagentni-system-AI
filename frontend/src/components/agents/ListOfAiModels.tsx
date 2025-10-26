/*
 * React component for displaying and managing the list of all AI models in the system.
 * Purpose:
 * - Shows all available AI models to the user and allows editing or deleting them.
 * Features:
 * - Fetches all AI models on mount using the AI model context.
 * - Displays model details: name and model identifier.
 * - Provides edit and delete buttons for each model.
 * - Edit action opens prompts to update model properties (name, identifier, API key).
 * Usage:
 * - Place this component on a page where you want to manage AI models.
 * - Requires the AI model context provider to be available.
 * Props: none
 */
import React, { useEffect } from "react";
import { useAI_Model } from '../../services/ai_modelContext';
import '../../css/Agent.css';

const ListOfAiModels: React.FC = () => {
  const { aiModels, fetchAIModels, updateAiModel, deleteAiModel } = useAI_Model();

  useEffect(() => {
    fetchAIModels();
  }, [fetchAIModels]);

  if (aiModels.length === 0) {
    return <div className="agents-item-empty">Zatím nemáte žádné AI modely</div>;
  }

  const handleEdit = (model: any) => {
    const safeValue = (val: any) => (val === null || val === undefined ? "" : val);

    const name = window.prompt("Zadejte nové jméno AI modelu:", safeValue(model.name));
    if (name === null) return;

    const model_identifier = window.prompt("Zadejte nový identifikátor modelu:", safeValue(model.model_identifier));
    if (model_identifier === null) return;

    const api_key = window.prompt("Zadejte nový váš API klíč:", safeValue(model.api_key));
    if (api_key === null) return;

    const updateData: any = {};

    if (name.trim() && name.trim() !== model.name) updateData.name = name.trim();
    if (model_identifier.trim() && model_identifier.trim() !== model.model_identifier)
      updateData.model_identifier = model_identifier.trim();
    if (api_key.trim() && api_key.trim() !== model.api_key) updateData.api_key = api_key.trim();

    if (Object.keys(updateData).length > 0) {
      console.log("🟢 Aktualizuji model:", updateData);
      updateAiModel(model.id, updateData);
    } else {
      console.log("ℹ️ Žádné změny nebyly provedeny.");
    }
  };

  return (
    <div className="list-of-ai-models">
      <h2><i className="bx bxs-brain"></i> Seznam AI modelů</h2>
      <ul className="ai-models-list">
        {aiModels.map((model) => (
          <li key={model.id} className="ai-model-item">
            <div className="ai-model-info">
              <strong>{model.name}</strong> <span>({model.model_identifier})</span>
            </div>
            <div className="ai-model-actions">
              <button id="btn-edit" onClick={() => handleEdit(model)}>
                <i className="bx bxs-pencil"></i>
              </button>
              <button id="btn-delete" onClick={() => deleteAiModel(model.id)}>
                <i className="bx bxs-trash"></i>
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ListOfAiModels;
