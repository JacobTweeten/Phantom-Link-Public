import React, { useState } from "react";
import { Form, Input, Button, notification } from "antd";
import { useNavigate } from "react-router-dom";

const VerifyEmailPage = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // Hook for navigation

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:5000/verify-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values), // { email, confirmation_code }
      });

      const data = await response.json();
      if (response.ok) {
        notification.success({
          message: "Success",
          description: data.message || "Email verified successfully!",
        });

        // Redirect to the login page after successful verification
        navigate("/login");
      } else {
        notification.error({
          message: "Error",
          description: data.error || "Verification failed. Please try again.",
        });
      }
    } catch (error) {
      console.error("Verification error:", error);
      notification.error({
        message: "Error",
        description: "An unexpected error occurred.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "50px auto" }}>
      <h2>Verify Your Email</h2>
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

        <Form.Item
          label="Confirmation Code"
          name="confirmation_code"
          rules={[{ required: true, message: "Please enter the confirmation code" }]}
        >
          <Input />
        </Form.Item>

        <Button type="primary" htmlType="submit" loading={loading}>
          Verify
        </Button>
      </Form>
    </div>
  );
};

export default VerifyEmailPage;
