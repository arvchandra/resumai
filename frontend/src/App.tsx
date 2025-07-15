import { BrowserRouter } from 'react-router-dom';

import AppRoutes from './routes/AppRoutes';
import { ResumesContextProvider } from "./contexts/ResumesContext";

import "./App.css";
import "./assets/styles/shared.css";

function App() {
  return (
    <BrowserRouter>
      <ResumesContextProvider>
        <AppRoutes />
      </ResumesContextProvider>
    </BrowserRouter>
  );
}

export default App;
