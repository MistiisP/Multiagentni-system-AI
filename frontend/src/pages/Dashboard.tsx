import React, { useEffect} from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../services/authContext';
import '../css/Dashboard.css';

import DashboardNavbar from '../components/DashboardNavbar';
import DashboardSideBar from '../components/DashboardSideBar';
import ChatCard from '../components/chat/ChatCard';
import LoadingLogo from '../components/LoadingLogo';
import NewChatCard from '../components/chat/NewChatCard';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [searchParams] = useSearchParams();
  const activeChatId = searchParams.get('chatId') ? Number(searchParams.get('chatId')) : null;

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
  }, [loading, user, navigate]);

  if (loading || user === undefined) {
    return <LoadingLogo />;
  }

  if (user) {
    return (
      <div className="dashboard-container">
        <DashboardSideBar />
        <DashboardNavbar />
        {activeChatId ? <ChatCard /> : <NewChatCard />}
      </div>
    );
  }
};

export default Dashboard;

