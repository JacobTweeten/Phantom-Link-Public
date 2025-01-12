import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Form, Input, Button, notification } from "antd";

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState(null);

  useEffect(() => {
    // Extract the token from the query parameters
    const resetToken = searchParams.get("token");
    if (resetToken) {
      setToken(resetToken);
    } else {
      notification.error({
        message: "Invalid Link",
        description: "No reset token provided. Please check your email link.",
      });
      navigate("/forgot-password");
    }
  }, [searchParams, navigate]);

  const onFinish = async (values) => {
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, password: values.password }),
      });

      const data = await response.json();

      if (response.ok) {
        notification.success({
          message: "Password Reset Successful",
          description: "Your password has been reset. You can now log in with your new password.",
        });
        navigate("/login");
      } else {
        notification.error({
          message: "Error",
          description: data.error || "Failed to reset password. Please try again.",
        });
      }
    } catch (err) {
      console.error("Error resetting password:", err);
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
      <h2>Reset Password</h2>
      <p>Please enter your new password below:</p>
      <Form onFinish={onFinish}>
        <Form.Item
          label="New Password"
          name="password"
          rules={[
            { required: true, message: "Please enter your new password" },
            { min: 8, message: "Password must be at least 8 characters long" },
          ]}
        >
          <Input.Password />
        </Form.Item>
        <Button type="primary" htmlType="submit" loading={loading}>
          Reset Password
        </Button>
      </Form>
    </div>
  );
};

export default ResetPassword;
