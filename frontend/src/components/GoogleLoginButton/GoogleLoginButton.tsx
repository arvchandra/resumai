import { useEffect } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../contexts/AuthContext';

export default function GoogleLoginButton() {
  const navigate = useNavigate();
  const { isAuthenticated, login, logout } = useAuth();

  // If already logged-in, redirect to tailor resume page
  // useEffect(() => {
  //   if (isAuthenticated) {
  //     navigate("/tailor-resume");
  //   }
  // }, [isAuthenticated, navigate]);

  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      const googleAccessToken = tokenResponse.access_token;

      try {
        const response = await fetch('http://localhost:8000/auth/google-login/', {
          method: 'POST',
          credentials: "include",
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ googleAccessToken: googleAccessToken }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Login failed');
        }

        const data = await response.json();
        login(data.accessToken, data.userInfo);
        navigate("/tailor-resume");
      } catch (error) {
        logout();
        console.error('Login error:', error);
      }
    },
    onError: () => console.error('Google Login Failed'),
  });

  return (
    <>
      <button className='btn btn-primary' onClick={() => googleLogin()}>Login with Google</button>
      <button className='btn btn-cancel' onClick={logout}>logout</button>
    </>
  )
}
