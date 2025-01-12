import React, { useState } from 'react';
import { Button, notification } from 'antd';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    try {
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
        credentials: 'include', // To send cookies for session handling
      });

      const data = await response.json();

      if (response.ok) {
        if (!data.is_email_verified) {
          // Redirect to verification page if email is not verified
          notification.warning({
            message: 'Email Not Verified',
            description:
              'Your email is not verified. Please enter the confirmation code sent to your email.',
          });

          // Call the send_confirmation_email endpoint to send the confirmation email
          await fetch('http://localhost:5000/api/send-confirmation-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: data.email }), // Send email in request body
            credentials: 'icnlude', // To send cookies for session handling
          });

          // Redirect to the verification page
          navigate('/verify', { state: { email: data.email } });
        } else {
          console.log('Login successful:', data);
          setSuccess(true);

          // Redirect to the homepage after a successful login
          navigate('/home');
        }
      } else {
        setError(data.error || 'Login failed. Please try again.');
        notification.error({
          message: 'Login Error',
          description: data.error || 'Login failed. Please try again.',
        });
      }
    } catch (err) {
      console.error('Error logging in:', err);
      notification.error({
        message: 'Error',
        description: 'An unexpected error occurred. Please try again later.',
      });
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '50px auto' }}>
      <h2>Login</h2>
      <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column' }}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          required
          style={{ marginBottom: '10px' }}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
          style={{ marginBottom: '10px' }}
        />
        <Button type="primary" htmlType="submit">
          Login
        </Button>
      </form>

      {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
      {success && <p style={{ color: 'green', marginTop: '10px' }}>Login successful!</p>}

      {/* Additional Links */}
      <div style={{ marginTop: '20px' }}>
        <span>Don’t have an account? </span>
        <Button type="link" onClick={() => navigate('/register')}>
          Create an Account
        </Button>
      </div>
      <div style={{ marginTop: '10px' }}>
        <Button type="link" onClick={() => navigate('/forgot-password')}>
          Forgot Password?
        </Button>
      </div>
    </div>
  );
};

export default Login;
