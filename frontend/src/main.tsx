import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import App from './App.tsx'
import { ResumesContextProvider } from "./contexts/ResumesContext";

import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ResumesContextProvider>
      <App />
    </ResumesContextProvider>
  </StrictMode>,
)
