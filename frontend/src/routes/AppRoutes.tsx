import { Routes, Route } from "react-router-dom";

import ProtectedRoute from "./ProtectedRoute";

import ResumeTailorForm from "../components/ResumeTailorForm/ResumeTailorForm";
import LoginButton from "../components/GoogleLoginButton/GoogleLoginButton";
import Layout from "../components/Layout/Layout";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Layout is a wrapper/container for all pages */}
      <Route path="/" element={<Layout />}>
        <Route path="/login" element={<LoginButton />} />

        {/* All routes below require user to be authenticated */}
        <Route element={<ProtectedRoute />}>
          <Route path="/tailor-resume" element={<ResumeTailorForm />} />
        </Route>
      </Route>
    </Routes>
  );
}
