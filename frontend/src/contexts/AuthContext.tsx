import React, { createContext, useContext, useEffect, useState } from "react";

interface AuthContextType {
  accessToken: string | null;
  setAccessToken: (token: string | null) => void;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessToken] = useState<string | null>(null);

  // Use refresh token, if it exists, to generate a new
  // access token on page load or refresh.
  useEffect(() => {
    const tryRefreshToken = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/auth/token/refresh/", {
          method: "POST",
          credentials: "include", // Sends refresh token cookie
        });

        if (res.ok) {
          const data = await res.json();
          setAccessToken(data.access); // restore access token in context
        } else {
          setAccessToken(null); // still unauthenticated
        }
      } catch {
        setAccessToken(null);
      }
    };

    tryRefreshToken();
  }, []);


  const contextValue: AuthContextType = {
    accessToken,
    setAccessToken,
    isAuthenticated: !!accessToken,
  }

  return (
    <AuthContext.Provider value={contextValue} >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuthContext must be used within AuthProvider');
  return context;
};
