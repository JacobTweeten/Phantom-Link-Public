import React from "react";
import { Layout, Menu, Typography, Button, Space, notification } from "antd";
import {
  SearchOutlined,
  InfoCircleOutlined,
  EnvironmentOutlined
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

const { Header, Content, Footer } = Layout;
const { Title, Paragraph } = Typography;

const HomePage = () => {
  const navigate = useNavigate();

  const sendLocationToServer = () => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;

          // Send location data to the backend
          fetch("http://localhost:5000/api/location", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              latitude: latitude,
              longitude: longitude,
              location_allowed: true,
            }),
          })
            .then((response) => response.json())
            .then((data) => {
              console.log("Location saved:", data);
              notification.success({
                message: "Location Shared",
                description: "Location has been successfully shared!",
              });
            })
            .catch((error) => {
              console.error("Error saving location:", error);
              notification.error({
                message: "Error",
                description: "There was an error sharing your location.",
              });
            });
        },
        (error) => {
          console.error("Geolocation error:", error);
          notification.error({
            message: "Geolocation Error",
            description: "Unable to retrieve your location.",
          });
        }
      );
    } else {
      console.log("Geolocation is not supported by this browser.");
      notification.error({
        message: "Unsupported Feature",
        description: "Geolocation is not supported by this browser.",
      });
    }
  };

  const openNotification = () => {
    notification.info({
      message: "About Phantom-Link",
      description: "Phantom-Link connects you with the past through the spirits of historical figures.",
    });
  };

  return (
    <Layout className="layout" style={{ minHeight: "100vh" }}>
      {/* Header */}
      <Header>
        <div className="logo" style={{ color: "white", fontSize: "1.5rem" }}>
          Phantom-Link
        </div>
        <Menu theme="dark" mode="horizontal" defaultSelectedKeys={["1"]}>
          <Menu.Item key="1" onClick={() => navigate("/")}>
            Home
          </Menu.Item>
          <Menu.Item key="2" onClick={() => navigate("/chat-history")}>
            Chat History
          </Menu.Item>
          <Menu.Item key="3">Features</Menu.Item>
        </Menu>
      </Header>

      {/* Content */}
      <Content style={{ padding: "50px", textAlign: "center" }}>
        <Space direction="vertical" size="large" align="center">
          <Title level={1}>Explore the Spirits Around You</Title>
          <Paragraph>
            Use Phantom-Link to connect with the ghosts of historical figures
            near your location. Discover hidden stories from the past.
          </Paragraph>

          {/* CTA Buttons */}
          <Space size="large">
            <Button
              type="primary"
              size="large"
              icon={<SearchOutlined />}
              onClick={async () => {
                try {
                  const response = await fetch("http://localhost:5000/api/reset-session", {
                    method: "POST",
                    credentials: "include",  // Ensure cookies are sent
                  });
                  const data = await response.json();
                  console.log("Session reset response:", data);
                } catch (error) {
                  console.error("Failed to reset session:", error);
                }
                navigate("/chat");
              }}
            >
              Find Ghosts
            </Button>

            <Button
              type="default"
              size="large"
              icon={<InfoCircleOutlined />}
              onClick={openNotification}
            >
              Learn More
            </Button>
            <Button
              type="default"
              size="large"
              icon={<EnvironmentOutlined />}
              onClick={sendLocationToServer}
            >
              Share Location
            </Button>
          </Space>
        </Space>
      </Content>

      {/* Footer */}
      <Footer style={{ textAlign: "center" }}>
        Phantom-Link 2025 Created by Jacob Tweeten
      </Footer>
    </Layout>
  );
};

export default HomePage;
