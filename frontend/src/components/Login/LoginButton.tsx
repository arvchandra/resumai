import { useGoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../contexts/AuthContext';

export default function LoginButton() {
  const navigate = useNavigate();
  const { setAccessToken } = useAuth();

  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      const googleAccessToken = tokenResponse.access_token;

      try {
        const response = await fetch('http://localhost:8000/auth/google-login/', {
          method: 'POST',
          credentials: "include",
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ google_access_token: googleAccessToken }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Login failed');
        }

        const data = await response.json();
        setAccessToken(data.accessToken);
        navigate("/tailor-resume");
      } catch (error) {
        setAccessToken(null);
        console.error('Login error:', error);
      }
    },
    onError: () => console.error('Google Login Failed'),
  });

  return <button className='btn btn-primary' onClick={() => login()}>Login with Google</button>;
}