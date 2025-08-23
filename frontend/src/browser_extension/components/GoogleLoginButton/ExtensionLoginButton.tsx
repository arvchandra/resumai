import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { useAuthApi } from "../../../api/authApi";
import { useAuth } from "../../../contexts/AuthContext";

export default function ExtensionLoginButton() {
  const navigate = useNavigate();
  const { accessToken, isAuthenticated, login, logout } = useAuth();
  const { login: apiLogin } = useAuthApi();

  console.log(`accessToken: ${accessToken}`);

  // If already logged-in, redirect to tailor resume page
  useEffect(() => {
    console.log(`authenticated: ${isAuthenticated}`);
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated]);

  const handleLogin = () => {
    chrome.runtime.sendMessage({ type: "GOOGLE_LOGIN" }, async (tokenResponse) => {
      const googleAccessToken = tokenResponse?.token;

      if (googleAccessToken) {
        try {
          const response = await apiLogin(googleAccessToken);

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Login failed");
          }

          const data = await response.json();
          console.log(data.access_token);
          console.log(data.userInfo);
          login(data.accessToken, data.userInfo);
          navigate("/");
        } catch (error) {
          logout();
          console.error("Login error:", error);
        }
      } else {
        console.error("Login failed:", tokenResponse?.error);
      }
    });
  };

  return (
    <div>
      {isAuthenticated && <div>Logged In!</div>}
      {!isAuthenticated &&
        <div className="btn-action-row">
          <button className="btn btn-primary" onClick={handleLogin}>Login with Google</button>
          <button className="btn btn-cancel" onClick={logout}>Logout</button>
        </div>
      }
    </div>
  )
}
