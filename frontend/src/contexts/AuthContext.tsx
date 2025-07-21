import React, { createContext, useContext, useState } from "react";

interface User {
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
  login: (newAccessToken: string, userInfo: User) => void;
  logout: () => void;
  refreshLogin: () => Promise<RefreshTokenResponse | null>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<User | null>(null);

  const login = (token: string, user: User) => {
    setAccessToken(token);
    setUserInfo(user);
    sessionStorage.setItem("userInfo", JSON.stringify(user));
  }

  const logout = async () => {
    setAccessToken(null);
    setUserInfo(null);
    sessionStorage.removeItem("userInfo");

    await fetch("http://localhost:8000/auth/logout/", {
      method: "POST",
      credentials: "include", // This includes the refresh token cookie with the request
    });
  }

  const refreshLogin = async (): Promise<RefreshTokenResponse | null> => {
    const response = await fetch("http://localhost:8000/auth/token/refresh/", {
      method: "POST",
      credentials: "include", // This includes the refresh token cookie with the request
    });

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
