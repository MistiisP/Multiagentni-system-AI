import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../../css/User.css';
import {useAuth} from "../../services/authContext";

const UnLogInButton: React.FC = () => {
  const navigate = useNavigate();
  const {logout} = useAuth();

  const handleUnLogin = () => {
    logout();
    navigate('/home');
  };

  return (
    <button className="unlogin-button" onClick={handleUnLogin}>
      <i className='bx bx-door-open'></i>
    </button>
  );
};

export default UnLogInButton;

