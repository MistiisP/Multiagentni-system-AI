import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import '../css/Home.css';

const NavbarHome: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    }
    
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [menuRef]);

  const toggleMenu = () => {
    const newState = !isMenuOpen;
    console.log("Menu je nyní: ", newState ? "otevřené" : "zavřené");
    setIsMenuOpen(newState);
  };

  return (
    <div className="navbar-container">
      <nav className="navbarHome">
        <div className="logo-circle">
          <img src="/src/assets/logo.png" alt="Logo" />
        </div>
        <div className="navbarHome-title">
          <h1>Multi Agent System</h1>
        </div>
        <div className="navbarHome-menu" ref={menuRef}>
          <button  className={`hamburger-icon ${isMenuOpen ? 'active' : ''}`} onClick={toggleMenu} aria-label="Menu">
            <span className="hamburger-line"></span>
            <span className="hamburger-line"></span>
            <span className="hamburger-line"></span>
          </button>
          
          {isMenuOpen && (
            <div className="dropdown-menu">
              <Link to="/about" onClick={toggleMenu}>About</Link>
              <Link to="/login" onClick={toggleMenu}>Log In</Link>
              <Link to="/signup" onClick={toggleMenu}>Sign Up</Link>
              <Link to="/dashboard" onClick={toggleMenu}>Dashboard</Link>
            </div>
          )}
        </div>
      </nav>
      <div className="navbar-border"></div>
    </div>
  );
};

export default NavbarHome;