/*
 * React context for managing authentication and user state in the application.
 * Purpose:
 * - Centralizes all authentication logic, including login, logout, registration, and user verification.
 * - Provides state and functions for accessing the current user, authentication token, and handling authentication errors.
 * Features:
 * - Handles user login with credentials and stores the authentication token in localStorage.
 * - Handles user registration.
 * - Automatically verifies and loads the current user on app load or token change.
 * - Provides logout functionality that clears user data and token.
 * - Manages loading and error states for authentication operations.
 * Usage:
 * - Wrap your application (or relevant part) with <AuthProvider>.
 * - Access authentication state and functions in components using the useAuth() hook.
 * Provided context value:
 * - user: The currently authenticated user (or null if not authenticated).
 * - token: The authentication token (or null if not authenticated).
 * - loading: Boolean indicating if authentication state is being loaded or verified.
 * - error: Error message, if any.
 * - login: Stores a new authentication token.
 * - logout: Logs out the user and clears authentication state.
 * - loginWithCredentials: Authenticates the user with username and password.
 * - registerUser: Registers a new user with name, email, and password.
 */
import React, { useState, useEffect, createContext, useContext, type ReactNode } from 'react';

interface UserData {
  id: number;
  name: string;
  email: string;
}

interface AuthContextType {
  user: UserData | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (newToken: string) => void;
  logout: () => void;
  loginWithCredentials: (username: string, password: string) => Promise<void>;
  registerUser: (data: { name: string; email: string; password: string }) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserData | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(true); 
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const verifyUser = async () => {
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }

      try {
        setError(null);
        const response = await fetch('http://127.0.0.1:8000/users/me', {
          headers: { 'Authorization': `Bearer ${token}` },
        });

        if (!response.ok) {
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
          throw new Error('Ověření selhalo, přihlaste se prosím znovu.');
        }

        const userData = await response.json();
        setUser(userData);
      } catch (err: any) {
        setError(err.message);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    verifyUser();
  }, [token]);



  const loginWithCredentials = async (username: string, password: string) => {
    setError(null);
    const response = await fetch('http://127.0.0.1:8000/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username, password }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Login failed');
    }
    login(data.access_token);
  };

  const registerUser = async (data: { name: string; email: string; password: string }) => {
    const response = await fetch('http://127.0.0.1:8000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorDetail;
      try {
        const errorData = JSON.parse(errorText);
        errorDetail = errorData.detail;
      } catch (e) {
        errorDetail = 'Unknown registration error';
      }
      throw new Error(errorDetail || 'Registration failed');
    }
  };


  const login = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  }

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  }

  const value = { user, loading, error, token, logout, login, loginWithCredentials, registerUser };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};