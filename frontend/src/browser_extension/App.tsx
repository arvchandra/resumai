import { HashRouter } from "react-router-dom";

import AppRoutes from "./routes/AppRoutes";
import { ResumesContextProvider } from "../contexts/ResumesContext";

import "./App.css";
import "../assets/styles/shared.css";
import { AuthProvider } from "../contexts/AuthContext";

function App() {
  return (
      <AuthProvider>
        <HashRouter>
          <ResumesContextProvider>
            <AppRoutes />
          </ResumesContextProvider>
        </HashRouter>
      </AuthProvider>
  );
}

export default App;
