import { BrowserRouter } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";

import AppRoutes from "./routes/AppRoutes";
import { ResumesContextProvider } from "./contexts/ResumesContext";
import { TailoredResumesContextProvider } from "./contexts/TailoredResumesContext";

import "./App.css";
import "./assets/styles/shared.css";
import { AuthProvider } from "./contexts/AuthContext";

const GOOGLE_OAUTH_CLIENT_ID = import.meta.env.VITE_GOOGLE_OAUTH_CLIENT_ID;

function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_OAUTH_CLIENT_ID}>
      <AuthProvider>
        <BrowserRouter>
          <ResumesContextProvider>
            <TailoredResumesContextProvider>
              <AppRoutes />
            </TailoredResumesContextProvider>
          </ResumesContextProvider>
        </BrowserRouter>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
