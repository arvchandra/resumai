import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';

import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = () => {
  const { accessToken, isAuthenticated, refreshLogin } = useAuth();

  const [checkingAuth, setCheckingAuth] = useState(true);
  const [refreshAttempted, setRefreshAttempted] = useState(false);

  // If access token is expired or not present, 
  // attempt one refresh of access token.
  useEffect(() => {
    const refreshAccessTokenIfNeeded = async () => {
      if (!accessToken && !refreshAttempted) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        await refreshLogin();
        setRefreshAttempted(true);
        setCheckingAuth(false);
      } else {
        // No need to refresh, access token is already set or refresh already attempted
        setCheckingAuth(false);
      }
    };

    refreshAccessTokenIfNeeded();
  }, [accessToken, refreshAttempted, refreshLogin]);

  if (checkingAuth) {
    return <div>Checking authentication...</div>; // Loading spinner placeholder
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
