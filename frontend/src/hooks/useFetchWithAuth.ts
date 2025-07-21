import { useAuth } from "../contexts/AuthContext";

export default function useFetchWithAuth() {
  const { accessToken, refreshLogin } = useAuth();

  const fetchWithAuth = async (
    url: string,
    init: RequestInit = {},
    retry = true
  ): Promise<Response> => {
    const headers = new Headers(init.headers || {});
    if (accessToken) {
      headers.set("Authorization", `Bearer ${accessToken}`);
    }

    const response = await fetch(url, {
      ...init,
      headers,
      credentials: "include", // This includes the refresh token cookie with the request
    });

    // If access token is expired, try refreshing once
    if (response.status === 401 && retry) {
      const newAccessToken = await refreshLogin();

      if (newAccessToken) {
        // Retry original request with new access token
        headers.set("Authorization", `Bearer ${newAccessToken}`);
        return fetch(url, {
          ...init,
          headers,
          credentials: "include", // This includes the refresh token cookie with the request
        });
      }
    }

    return response;
  };

  return fetchWithAuth;
};
