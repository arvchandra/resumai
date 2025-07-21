import React, { createContext, useContext, useState } from "react";

interface AuthContextType {
  accessToken: string | null;
  isAuthenticated: boolean;
  setAccessToken: (token: string | null) => void;
  refreshLogin: () => Promise<string | null>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessToken] = useState<string | null>(null);

  const refreshLogin = async (): Promise<string | null> => {
    const response = await fetch("http://localhost:8000/auth/token/refresh/", {
      method: "POST",
      credentials: "include", // This includes the refresh token cookie with the request
    });

    if (response.ok) {
      const data = await response.json();

      if (data.accessToken) {
        setAccessToken(data.accessToken);
        return data.accessToken;
      }
    }

    return null;
  };

  const contextValue: AuthContextType = {
    accessToken,
    isAuthenticated: !!accessToken,
    setAccessToken,
    refreshLogin,
  }

  return (
    <AuthContext.Provider value={contextValue} >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuthContext must be used within AuthProvider");
  return context;
};
