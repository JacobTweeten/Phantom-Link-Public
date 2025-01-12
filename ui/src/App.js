// App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./components/HomePage";
import ChatPage from "./components/ChatPage";
import Login from "./components/accountPages/Login";
import RegisterPage from "./components/accountPages/RegisterPage";
import Verification from './components/accountPages/Verification';
import ForgotPassword from './components/accountPages/ForgotPassword';
import ResetPassword from './components/accountPages/ResetPassword';
import WelcomePage from './components/WelcomePage';
import ChatHistory from './components/ChatHistory';

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<WelcomePage />} />
      <Route path="/home" element={<HomePage />} />
      <Route path="/chat" element={<ChatPage />} />
      <Route path = "/login" element={<Login />} />
      <Route path = "/register" element={<RegisterPage />} />
      <Route path = "/verify" element={<Verification />} />
      <Route path = "/forgot-password" element={<ForgotPassword />} />
      <Route path = "/reset-password" element={<ResetPassword />} />
      <Route path = "/chat-history" element={<ChatHistory />} />
    </Routes>
  </Router>
);

export default App;
