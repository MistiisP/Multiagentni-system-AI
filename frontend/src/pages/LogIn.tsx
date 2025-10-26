import React , {useEffect} from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/login/LoginForm';
import LoadingLogo from '../components/LoadingLogo';
import '../css/App.css';
import {useAuth} from '../services/authContext';

const LogIn: React.FC = () => {
  const {user, loading} = useAuth();
  const navigate = useNavigate();

  const pageStyle: React.CSSProperties = {
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: '10%',
    textAlign: 'center'
  };

  useEffect(() => {
    if (user) {
      navigate("/dashboard");
    }
  }, [user, navigate]);

  if (loading) {
    return (
      <LoadingLogo />
    );
  }

  return (
    <div className="login-page" style={pageStyle}>
      <LoginForm />
    </div>
  );
};

export default LogIn;