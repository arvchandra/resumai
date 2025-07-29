import React, { createContext, useContext, useState } from "react";

import { useUnauthenticatedApi } from "../api/api";

export interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
}

interface RefreshTokenResponse {
  accessToken: string;
  userInfo: User;
}

interface AuthContextType {
  accessToken: string | null;
  userInfo: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  refreshLogin: () => Promise<RefreshTokenResponse | null>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<User | null>(null);

  const { logout: apiLogout, refreshToken } = useUnauthenticatedApi();

  const login = (token: string, user: User) => {
    setAccessToken(token);
    setUserInfo(user);
  }

  const logout = async () => {
    setAccessToken(null);
    setUserInfo(null);

    await apiLogout();
  }

  const refreshLogin = async (): Promise<RefreshTokenResponse | null> => {
    const response = await refreshToken();

    if (response.ok) {
      const accessTokenAndUser: RefreshTokenResponse = await response.json();

      if (accessTokenAndUser) {
        login(accessTokenAndUser.accessToken, accessTokenAndUser.userInfo);
        return accessTokenAndUser;
      } else {
        logout();
      }
    }

    return null;
  };

  const contextValue: AuthContextType = {
    accessToken,
    userInfo,
    isAuthenticated: !!accessToken,
    login,
    logout,
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
