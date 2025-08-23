chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "GOOGLE_LOGIN") {
    const clientId = import.meta.env.VITE_GOOGLE_OAUTH_CLIENT_ID;
    const redirectUri = chrome.identity.getRedirectURL();

    const authUrl =
      "https://accounts.google.com/o/oauth2/v2/auth" +
      `?client_id=${clientId}` +
      `&response_type=token` +
      `&redirect_uri=${encodeURIComponent(redirectUri)}` +
      `&scope=${encodeURIComponent("openid profile email")}`;

    chrome.identity.launchWebAuthFlow(
      { url: authUrl, interactive: true },
      (redirectedTo) => {
        if (chrome.runtime.lastError) {
          sendResponse({ error: chrome.runtime.lastError });
          return;
        }

        // Extract access_token from URL fragment
        if (redirectedTo) {
          const params = new URLSearchParams(
            redirectedTo.split("#")[1] // after "#"
          );
          const accessToken = params.get("access_token");
          sendResponse({ token: accessToken });
        }
      }
    );

    return true; // Keep sendResponse async
  }

  if (message.type === "SET_COOKIE") {
    chrome.cookies.set(message.cookie, (cookie) => {
      console.log("Cookie set:", cookie);
      sendResponse({ success: true });
    });
    return true; // keep channel open for async response
  }
});
