import { useEffect } from "react";
import { useGoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";

import { useAuthApi } from "../../api/authApi";
import { useAuth } from "../../contexts/AuthContext";


export default function GoogleLoginButton() {
  const navigate = useNavigate();
  const { isAuthenticated, login, logout } = useAuth();
  const { login: apiLogin } = useAuthApi();

  // If already logged-in, redirect to tailor resume page
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/tailor-resume");
    }
  }, [isAuthenticated]);

  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      const googleAccessToken = tokenResponse.access_token;

      try {
        const response = await apiLogin(googleAccessToken);

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Login failed");
        }

        const data = await response.json();
        login(data.accessToken, data.userInfo);
        navigate("/tailor-resume");
      } catch (error) {
        logout();
        console.error("Login error:", error);
      }
    },
    onError: () => console.error("Google Login Failed"),
  });

  return (
    <div className="btn-action-row">
      <button className="btn btn-primary" onClick={() => googleLogin()}>Login with Google</button>
      <button className="btn btn-cancel" onClick={logout}>Logout</button>
    </div>
  )
}
