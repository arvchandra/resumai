import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';

import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = () => {
  const { isAuthenticated, refreshLogin } = useAuth();

  const [checkingAuth, setCheckingAuth] = useState(true);

  // If access token is expired or not present, 
  // attempt one refresh of access token.
  useEffect(() => {
    const refreshAccessTokenIfNeeded = async () => {
      if (!isAuthenticated) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        await refreshLogin();
      }
      setCheckingAuth(false);
    };

    refreshAccessTokenIfNeeded();
  });

  if (checkingAuth) {
    return <div>Checking authentication...</div>; // Loading spinner placeholder
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
