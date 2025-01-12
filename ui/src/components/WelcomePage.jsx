import React, { useState } from 'react';
import { Button, notification } from 'antd';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Redirect to home page after successful login
        navigate('/home');
      } else {
        setError(data.error || 'Login failed. Please try again.');
        notification.error({
          message: 'Login Error',
          description: data.error || 'Login failed. Please try again.',
        });
      }
    } catch (err) {
      console.error('Login error:', err);
      notification.error({
        message: 'Error',
        description: 'An unexpected error occurred.',
      });
    }
  };

  // Redirect to the login page
  const redirectToLogin = () => {
    navigate('/login');
  };

  return (
    <div style={{ maxWidth: 400, margin: '50px auto' }}>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <Button type="primary" htmlType="submit">
          Login
        </Button>
      </form>

      <Button
        type="default"
        style={{ marginTop: '10px' }}
        onClick={redirectToLogin}
      >
        Redirect to Login Page
      </Button>

      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default Login;
