import React from 'react';
import NavbarHome from '../components/NavbarHome';
import LoginForm from '../components/login/LoginForm';
import Footer from '../components/Footer';
import LoadingLogo from '../components/LoadingLogo';
import '../css/Home.css';
import '../css/App.css';
import {useAuth} from '../services/authContext';
import {Link} from 'react-router-dom';

const Home: React.FC = () => {
  const {user, loading} = useAuth();

  if (loading) {
    return (
      <LoadingLogo />
    );
  }

  if (user) {
    return (
      <div className="home-container">
        <NavbarHome />
        <div className="home-content">
          <h1>Vítejte v Multi Agent Systému</h1>
          <p> Už jste přihlášen, <Link to="/dashboard">pokračujte</Link>.</p>
          <Footer />
        </div>
      </div>
    );
  }


  return (
    <div className="home-container">
      <NavbarHome />
      <div className="home-content">
        <h1>Vítejte v Multi Agent Systému</h1>
        <p>Prosím přihlašte se nebo zaregistrujte pro pokráčování.</p>
        <LoginForm />
        <Footer />
      </div>
    </div>
  );
};

export default Home;