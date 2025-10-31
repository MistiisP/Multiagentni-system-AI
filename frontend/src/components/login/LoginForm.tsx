import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../css/User.css';
import 'boxicons/css/boxicons.min.css';
import { useAuth } from '../../services/authContext';

const LoginForm: React.FC = () => {
  const {loginWithCredentials} = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await loginWithCredentials(username, password);
      navigate('/dashboard');
    } catch (error: any) {
      setError(error.message || 'Špatné heslo');
    }
  };

  return (
    <div className="login-container">
      <h2>Přihlášení</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <input type="text" id="username" value={username} placeholder="Username" onChange={(e) => setUsername(e.target.value)} required />
          <i className="bx bx-user"></i>
        </div>
        <div className="form-group">
          <input type="password" id="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required/>
          <i className="bx bx-lock-alt"></i> 
        </div>
        <button type="submit">Přihlásit</button>
          {error && (
            <div className="error-message" style={{ color: 'red', marginTop: '10px', fontWeight: '500' }}>
              {error}
            </div> 
          )}
      </form>
      <p>Nemáte účet?<a href="/signup"> Zaregistrujte se</a></p>
    </div>
  );
};

export default LoginForm;