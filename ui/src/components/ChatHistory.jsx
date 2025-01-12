import React, { useEffect, useState } from "react";
import { Layout, Menu, Button, Space, notification, Card, Typography } from "antd";
import { useNavigate } from "react-router-dom";
import { UserOutlined } from "@ant-design/icons";

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const ChatHistory = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState(null);
  const [conversations, setConversations] = useState([]);

  // Check if the user is logged in
  useEffect(() => {
    const checkUserSession = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/me", {
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          if (data.username) {
            setUsername(data.username);
            fetchConversations(); // Fetch conversations for logged-in user
          } else {
            navigate("/login"); // Redirect to login if no user session found
          }
        }
      } catch (err) {
        console.error("Failed to check user session:", err);
        navigate("/login"); // Redirect to login if there's an error checking the session
      }
    };

    checkUserSession();
  }, [navigate]);

  // Fetch the conversations for the logged-in user
  const fetchConversations = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/conversations", {
        credentials: "include", // Ensure cookies are sent
      });
      if (res.ok) {
        const data = await res.json();
        setConversations(data.conversations);
      } else {
        notification.error({
          message: "Error",
          description: "Failed to load conversations.",
        });
      }
    } catch (err) {
      console.error("Error fetching conversations:", err);
      notification.error({
        message: "Error",
        description: "An unexpected error occurred.",
      });
    }
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/logout", {
        method: "POST",
        credentials: "include",
      });
      if (res.ok) {
        setUsername(null); // Clear local state
        navigate("/login"); // Redirect to login page after logout
      }
    } catch (err) {
      console.error("Logout error:", err);
    }
  };

  if (username === null) {
    // Show loading or placeholder while session is being checked
    return <div>Loading...</div>;
  }

  return (
    <Layout className="layout" style={{ minHeight: "100vh" }}>
      {/* Header */}
      <Header>
        <div className="logo" style={{ color: "white", fontSize: "1.5rem" }}>
          Phantom-Link
        </div>
        <Menu theme="dark" mode="horizontal" defaultSelectedKeys={["1"]}>
          <Menu.Item key="1">Home</Menu.Item>
          <Menu.Item key="2">Features</Menu.Item>

          {/* Link to Chat History */}
          <Menu.Item key="4" onClick={() => navigate("/chat-history")}>
            Chat History
          </Menu.Item>

          <Menu.Item key="3" style={{ marginLeft: "auto" }}>
            {username ? (
              <Space>
                <span style={{ color: "white" }}>Welcome, {username}!</span>
                <Button onClick={handleLogout}>Logout</Button>
              </Space>
            ) : (
              <Button
                type="default"
                icon={<UserOutlined />}
                onClick={() => navigate("/login")}
              >
                Login
              </Button>
            )}
          </Menu.Item>
        </Menu>
      </Header>

      {/* Content */}
      <Content style={{ padding: "50px", textAlign: "center" }}>
        <Title level={2}>Your Chat History</Title>

        {/* Display the conversations */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "20px", justifyContent: "center" }}>
          {conversations.length === 0 ? (
            <p>No conversations found. Start a chat with a ghost!</p>
          ) : (
            conversations.map((conversation, index) => (
              <Card
                key={index}
                title={`Conversation with: ${conversation.ghost_name || "Unknown"}`}
                style={{ width: "400px" }}
                hoverable
                onClick={() => navigate(`/chat/${conversation.id}`)} // Navigate to detailed view
              >
                <p>{conversation.chat_log.slice(0, 100)}...</p> {/* Show a preview of the chat */}
              </Card>
            ))
          )}
        </div>
      </Content>

      {/* Footer */}
      <Footer style={{ textAlign: "center" }}>
        Phantom-Link 2025 Created by Jacob Tweeten
      </Footer>
    </Layout>
  );
};

export default ChatHistory;
