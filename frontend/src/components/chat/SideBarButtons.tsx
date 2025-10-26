import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../../css/Chat.css';
import 'boxicons/css/boxicons.min.css'; 
import {useChat} from '../../services/chatContext';

const SideBarButtons: React.FC = () => {
  const {selectChat} = useChat();
  const navigate = useNavigate();

  const handleNewChat = () => {
    navigate(`/dashboard?new-chat`);
    selectChat(null);
  };
  
  const handleAgentSettings = () => {
    navigate('/settings?tab=agents');
  };

  const handleGraphsExecutionSettings = () => {
    navigate('/settings?tab=graphs_execution');
  };

  return (
    <>
    <button className="sidebar-buttons" onClick={handleNewChat}>
      <i className='bx bx-edit'></i>  Nová konverzace
    </button>
    <button className="sidebar-buttons" onClick={handleAgentSettings}>
        <i className='bx bxs-mask'></i> Nastavení agentů
    </button>
    <button className="sidebar-buttons" onClick={handleGraphsExecutionSettings}>
      <i className='bx bx-bar-chart'></i>Analýza běhu grafů 
    </button>
    </>
  );
};

export default SideBarButtons;