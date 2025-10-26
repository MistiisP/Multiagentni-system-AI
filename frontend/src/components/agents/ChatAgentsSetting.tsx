import React, { useEffect } from 'react';
import '../../css/Chat.css';
import ChatListOfAgents from './ChatListOfAgents';
import ChatManageAgents from './ChatManageAgents';
import GraphVisualizer from './GraphVisualizer';
import WorkflowBuilder from './WorkFlowBuilder';
import { useGraph } from '../../services/graphContext';

interface ChatAgentsSettingsProps {
  activeChatId: number;
  activeGraphId: number | null;
}

const ChatAgentsSetting: React.FC<ChatAgentsSettingsProps> = ({ activeChatId }) => {
  const { graphId, setGraphId, setActiveChatId } = useGraph();

  useEffect(() => {
    setActiveChatId(activeChatId)
  }, [activeChatId, setGraphId]);

  return (
    <div className="chat-agents-setting">
      <ChatListOfAgents chatId={activeChatId} />
      <ChatManageAgents chatId={activeChatId} />
      <GraphVisualizer graphId={graphId}/>
      <WorkflowBuilder chatId={activeChatId} />
    </div>
  );
};

export default ChatAgentsSetting;