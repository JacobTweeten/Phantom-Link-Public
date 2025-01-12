import React, { useState } from "react";
import { Form, Input, Button, notification } from "antd";
import { useNavigate } from "react-router-dom";

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    const { email } = values; // Extract email from form values
    setLoading(true);
  
    try {
      const response = await fetch("http://localhost:5000/api/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }), // Now this will have the email value
      });
  
      const data = await response.json();
  
      if (response.ok) {
        notification.success({
          message: "Email Sent",
          description: "A password reset email has been sent. Please check your inbox.",
        });
        navigate("/login"); // Redirect to login page after sending the email
      } else {
        notification.error({
          message: "Error",
          description: data.error || "Failed to send reset email. Please try again.",
        });
      }
    } catch (err) {
      console.error("Error sending reset email:", err);
      notification.error({
        message: "Error",
        description: "An unexpected error occurred. Please try again later.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "50px auto" }}>
      <h2>Forgot Password</h2>
      <p>Please enter your email address. We will send you a link to reset your password.</p>
      <Form onFinish={onFinish}>
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
        <Button type="primary" htmlType="submit" loading={loading}>
          Send Reset Link
        </Button>
      </Form>
    </div>
  );
};

export default ForgotPassword;
