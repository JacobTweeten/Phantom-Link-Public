import React, { useState } from "react";
import { Layout, Form, Input, Button, Typography, notification } from "antd";
import { useNavigate } from "react-router-dom";

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const RegisterPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);

    try {
      // 1) Register the user
      const registerResponse = await fetch("http://localhost:5000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values), // { username, email, password }
        credentials: "include",
      });

      if (!registerResponse.ok) {
        const errorData = await registerResponse.json();
        throw new Error(errorData.error || "Registration failed");
      }

      const registerData = await registerResponse.json();
      console.log("User registered successfully:", registerData);

      notification.success({
        message: "Success",
        description: registerData.message || "User registered successfully",
      });

      // 2) Call /send-confirmation-email to send the verification code
      const emailResponse = await fetch("http://localhost:5000/send-confirmation-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: values.email }), // Send email in request body
        credentials: "include",
      });

      if (!emailResponse.ok) {
        const errorData = await emailResponse.json();
        throw new Error(errorData.error || "Failed to send email");
      }

      const emailData = await emailResponse.json();
      console.log("Confirmation email sent:", emailData);

      notification.info({
        message: "Verification Email Sent",
        description: "We’ve sent a confirmation code to your email. Please check your inbox.",
      });

      // 3) Redirect to the verification page
      navigate("/verify", { state: { email: values.email } }); // Pass the email to the verification page
    } catch (error) {
      console.error("Error in registration or emailing:", error);
      notification.error({
        message: "Error",
        description: error.message || "An unexpected error occurred",
      });
    } finally {
      setLoading(false);
    }
  };

  const formItemLayout = {
    labelCol: { span: 8 },
    wrapperCol: { span: 16 },
  };

  return (
    <Layout className="layout" style={{ minHeight: "100vh" }}>
      <Header>
        <div style={{ color: "white", fontSize: "1.5rem" }}>Phantom-Link</div>
      </Header>

      <Content style={{ padding: "50px" }}>
        <div style={{ maxWidth: "500px", margin: "0 auto" }}>
          <Title level={2}>Create Account</Title>
          <Form
            {...formItemLayout}
            name="registerForm"
            onFinish={onFinish}
            layout="horizontal"
          >
            <Form.Item
              label="Username"
              name="username"
              rules={[
                { required: true, message: "Please enter your username" },
              ]}
            >
              <Input />
            </Form.Item>

            <Form.Item
              label="Email"
              name="email"
              rules={[
                { required: true, message: "Please enter your email" },
                { type: "email", message: "Please enter a valid email" },
              ]}
            >
              <Input />
            </Form.Item>

            <Form.Item
              label="Password"
              name="password"
              rules={[{ required: true, message: "Please enter your password" }]}
            >
              <Input.Password />
            </Form.Item>

            <Form.Item wrapperCol={{ span: 16, offset: 8 }}>
              <Button type="primary" htmlType="submit" loading={loading}>
                Register
              </Button>
            </Form.Item>
          </Form>
        </div>
      </Content>

      <Footer style={{ textAlign: "center" }}>
        Phantom-Link 2025 Created by Jacob Tweeten
      </Footer>
    </Layout>
  );
};

export default RegisterPage;
