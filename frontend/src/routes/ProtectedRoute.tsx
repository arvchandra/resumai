import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const getNewAccessToken = async () => {
  const refreshResponse = await fetch("http://localhost:8000/auth/token/refresh/", {
    method: "POST",
    credentials: "include",
  });

  if (refreshResponse.ok) {
    const data = await refreshResponse.json();
    const newAccessToken = data.accessToken;
    return newAccessToken;
  }

  return null;
};

const ProtectedRoute = () => {
  const { accessToken, setAccessToken, isAuthenticated } = useAuth();

  const [checkingAuth, setCheckingAuth] = useState(true);
  const [refreshAttempted, setRefreshAttempted] = useState(false);

  useEffect(() => {
    const refreshIfNeeded = async () => {
      if (!accessToken && !refreshAttempted) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        const newAccessToken = await getNewAccessToken();
        if (newAccessToken) {
          setAccessToken(newAccessToken);
        }
        setRefreshAttempted(true);
        setCheckingAuth(false);
      } else {
        // No need to refresh, accessToken is already set or refresh already tried
        setCheckingAuth(false);
      }
    };

    refreshIfNeeded();
  }, [accessToken, refreshAttempted, setAccessToken]);

  if (checkingAuth) {
    return <div>Checking authentication...</div>; // Loading spinner placeholder
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;