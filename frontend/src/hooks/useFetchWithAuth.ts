import { useAuth } from "../contexts/AuthContext";

export default function useFetchWithAuth() {
  const { accessToken, setAccessToken } = useAuth();

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
      const refreshResponse = await fetch("http://localhost:8000/auth/token/refresh/", {
        method: "POST",
        credentials: "include",
      });

      if (refreshResponse.ok) {
        const data = await refreshResponse.json();
        const newAccessToken = data.accessToken;
        setAccessToken(newAccessToken);

        // Retry original request with new access token
        headers.set("Authorization", `Bearer ${newAccessToken}`);
        return fetch(url, {
          ...init,
          headers,
          credentials: "include",
        });
      }
    }

    return response;
  };

  return fetchWithAuth;
};
