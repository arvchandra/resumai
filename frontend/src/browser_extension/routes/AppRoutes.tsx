import { Routes, Route } from "react-router-dom";

import LoginButton from "../components/GoogleLoginButton/ExtensionLoginButton";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LoginButton />} />
    </Routes>
  );
}
