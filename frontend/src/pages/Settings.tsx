import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import '../css/Settings.css';
import '../css/Agent.css';
import {useAuth} from '../services/authContext';

import UserBarDisplay from '../components/user/UserBarDisplay';
import AgentNewForm from '../components/agents/AgentNewForm';
import ListOfAgents from '../components/agents/ListOfAgents';
import ModelAINewForm from '../components/agents/ModelAINewForm';
import ListOfAiModels from '../components/agents/ListOfAiModels';
import GraphAnalysis from '../components/agents/GraphAnalysis';
import LoadingLogo from '../components/LoadingLogo';


const Settings: React.FC = () => {
  const navigate = useNavigate();
  const {loading, user} = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get("tab") || "agents";

  const handleNavigation = (tab: string) => {
    setSearchParams({tab});
  };

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
  }, [loading, user, navigate]);

  if (loading || user === undefined) {
    return <LoadingLogo />;
  }

  return (
    <div className="settings-page">
      <div className="settings-sidebar">
        <div className="settings-header">
            <UserBarDisplay />
        </div>
        <div className="settings-sidebar-content">
        <ul>
          <li className={activeTab === 'agents' ? 'active' : ''} onClick={() => handleNavigation('agents')} >
            Agenti
          </li>
          <li className={activeTab === 'graphs_execution' ? 'active' : ''} onClick={() => handleNavigation('graphs_execution')} >
            Analýza grafů
          </li>
        </ul>
          <div className="settings-backtoDashboard">
            <button className="back-button"onClick={() => navigate('/dashboard')}>Zpět na dashboard</button>
          </div>
        </div>
      </div>
      <div className="settings-main">
        {activeTab === 'agents' && <div>
          <ListOfAgents />
          <AgentNewForm />
          <ListOfAiModels />
          <ModelAINewForm />
        </div>}
        {activeTab === 'graphs_execution' && <div> 
          <GraphAnalysis />
        </div>}
      </div>
  </div>  
  );
};

export default Settings;