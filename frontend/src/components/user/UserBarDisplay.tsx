import React from 'react';
import UserAvatar from './UserAvatar';
import '../../css/User.css';
import { useAuth } from '../../services/authContext';

const UserBarDisplay: React.FC = () => {
  const { user, loading, error } = useAuth();

  return (
    <div className="user-bar-display">
      {loading ? (
        <div className="user-bar-loading">Načítání...</div>
      ) : error ? (
        <div className="user-bar-error">{error}</div>
      ) : user ? (
        <>
          <UserAvatar size="medium" color="primary" />
          <span className="user-name">{user.name || 'Uživatel'}</span>
        </>
      ) : (
        <div>Není přihlášen</div>
      )}
    </div>
  );
};

export default UserBarDisplay;