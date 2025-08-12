const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const AUTH_API_BASE_URL = `${API_BASE_URL}/auth`;

export function useAuthApi() {
  return { 
    login(googleAccessToken: string) {
      return fetch(`${AUTH_API_BASE_URL}/google-login/`, {
        method: "POST",
        credentials: "include", // This includes the refresh token cookie with the request
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ googleAccessToken: googleAccessToken }),
      });
    },
    logout() {
      return fetch(`${AUTH_API_BASE_URL}/logout/`, {
        method: "POST",
        credentials: "include", // This includes the refresh token cookie with the request
      });
    },
    refreshToken() {
      return fetch(`${AUTH_API_BASE_URL}/token/refresh/`, {
        method: "POST",
        credentials: "include", // This includes the refresh token cookie with the request
      });
    }
  };
}
