import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';

import { useAuth } from '../contexts/AuthContext';
import { getNewAccessToken } from '../hooks/useFetchWithAuth';

const ProtectedRoute = () => {
  const { accessToken, setAccessToken, isAuthenticated } = useAuth();

  const [checkingAuth, setCheckingAuth] = useState(true);
  const [refreshAttempted, setRefreshAttempted] = useState(false);

  // If access token is expired or not present, attempt one refresh
  // to get new access token.
  useEffect(() => {
    const refreshAccessTokenIfNeeded = async () => {
      if (!accessToken && !refreshAttempted) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        const newAccessToken = await getNewAccessToken();
        if (newAccessToken) {
          setAccessToken(newAccessToken);
        }
        setRefreshAttempted(true);
        setCheckingAuth(false);
      } else {
        // No need to refresh, accessToken is already set or refresh already attempted
        setCheckingAuth(false);
      }
    };

    refreshAccessTokenIfNeeded();
  }, [accessToken, refreshAttempted, setAccessToken]);

  if (checkingAuth) {
    return <div>Checking authentication...</div>; // Loading spinner placeholder
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
