import { useAuth } from "../contexts/AuthContext";

export type fetchWithAuthSignature = (
  url: string, 
  init?: RequestInit, 
  retry?: boolean,
) => Promise<Response>;

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
      const accessTokenAndUser = await refreshLogin();

      if (accessTokenAndUser) {
        // Retry original request with new access token
        headers.set("Authorization", `Bearer ${accessTokenAndUser.accessToken}`);
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
