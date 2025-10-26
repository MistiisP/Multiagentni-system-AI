import {Routes, Route} from "react-router-dom";

import Home from './pages/Home'
import LogIn from './pages/LogIn'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import { ChatProvider } from './services/chatContext';
import { useAuth } from "./services/authContext";
import { AgentProvider } from "./services/agentContext";
import { AI_ModelProvider } from "./services/ai_modelContext";
import { GraphProvider } from "./services/graphContext";
import { ToolsProvider } from "./services/toolsContext";

import 'boxicons/css/boxicons.min.css';
import './css/App.css'
import LoadingLogo from "./components/LoadingLogo";


function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingLogo />
  }

  if (!user) {
    return <LogIn />;
  }
  return (
    <ChatProvider>
      <AI_ModelProvider>
        <AgentProvider>
          <ToolsProvider>
            <GraphProvider>
              <main className='App'>
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/home" element={<Home />} />
                  <Route path="/login" element={<LogIn />} />
                  <Route path="/signup" element={<SignUp />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </main>
            </GraphProvider>
          </ToolsProvider>
        </AgentProvider>
      </AI_ModelProvider>
    </ChatProvider>
  )
}

export default App
