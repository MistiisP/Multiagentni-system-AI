import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import UnLogInButton from './login/UnLogInButton';
import UserBarDisplay from './user/UserBarDisplay';
import '../css/Dashboard.css';
import 'boxicons/css/boxicons.min.css';

const DashboardNavbar: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="dashboard-navbar-container">
      <nav className="dashboard-navbar">
      <div className="navbar-left">
        <div className="logo-circle">
          <img src="/src/assets/logo.png" alt="Logo" />
        </div>
        <span className="app-name"><Link to="/home" style={{ color: '#007bff'}}>Multi Agent System</Link></span>
      </div>
        <div className="navbar-right">
          <div className="avatar-container" onClick={() => navigate('/settings')}>
            <UserBarDisplay />
          </div>
          <UnLogInButton />
        </div>
      </nav>
    </div>
  );
};

export default DashboardNavbar;