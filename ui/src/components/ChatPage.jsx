import React, { useState } from "react";
import { Input, Button, List, Layout, notification } from "antd";
import { useNavigate } from "react-router-dom";

const { Header, Content, Footer } = Layout;

const ChatPage = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");

  // Function to send the user's message
  const handleSend = async () => {
    if (!userInput.trim()) return;

    // Add user message to chat
    setMessages((prev) => [...prev, { role: "user", content: userInput }]);

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userInput }),
        credentials: "include", // Ensure cookies are sent
      });

      const data = await response.json();
      if (data.reply) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply },
        ]);
      } else {
        console.error(data.error);
      }
    } catch (error) {
      console.error("Error:", error);
    }

    setUserInput("");
  };

  // Function to end the conversation and save it to the database
  const handleEndConversation = async () => {
    try {
      const response = await fetch("http://localhost:5000/end-conversation", {
        method: "POST",
        credentials: "include", // Ensure cookies are sent
      });

      const data = await response.json();
      if (data.message === "Conversation saved successfully.") {
        notification.success({
          message: "Conversation Ended",
          description: "Your conversation has been saved.",
        });
        // Redirect to home after ending the conversation
        navigate("/home");
      } else {
        // Log and display the error message from the backend
        console.error("Error from server:", data.error);
        notification.error({
          message: "Error",
          description: data.error || "There was an error ending the conversation.",
        });
      }
    } catch (error) {
      console.error("Error ending conversation:", error);
      notification.error({
        message: "Server Error",
        description: "There was an error with the server.",
      });
    }
  };

  return (
    <Layout style={{ height: "100vh" }}>
      <Header style={{ color: "white", fontSize: "1.5rem" }}>
        Chat with Phantom-Link
      </Header>
      <Content
        style={{
          padding: "24px",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
        }}
      >
        <List
          dataSource={messages}
          renderItem={(msg) => (
            <List.Item
              style={{ textAlign: msg.role === "user" ? "right" : "left" }}
            >
              <List.Item.Meta description={msg.content} />
            </List.Item>
          )}
        />
        <div style={{ display: "flex", gap: "10px" }}>
          <Input
            placeholder="Type your message..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onPressEnter={handleSend}
          />
          <Button type="primary" onClick={handleSend}>
            Send
          </Button>
        </div>
        <div style={{ marginTop: "20px" }}>
          <Button type="danger" onClick={handleEndConversation}>
            End Conversation
          </Button>
        </div>
      </Content>
      <Footer style={{ textAlign: "center" }}>
        Phantom-Link 2025 Created by Jacob Tweeten
      </Footer>
    </Layout>
  );
};

export default ChatPage;
