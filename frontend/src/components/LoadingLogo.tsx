import React from 'react';
import '../css/App.css';
import logoImg from '../assets/logo.png';

const LoadingLogo: React.FC = () => {
  return (
    <div className="loading-logo">
      <img src={logoImg} alt="Logo" style={{ width: 128, height: 128 }} />
      <div className="loading-text">Loading...</div>
    </div>
  );
};

export default LoadingLogo;