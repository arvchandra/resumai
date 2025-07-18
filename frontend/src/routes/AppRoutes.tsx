import { Routes, Route } from 'react-router-dom';

import ProtectedRoute from './ProtectedRoute';

import ResumeTailorForm from '../components/ResumeTailorForm/ResumeTailorForm';
import LoginButton from '../components/Login/LoginButton';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginButton />} />

      {/* All routes below require user to be authenticated */}
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<ResumeTailorForm />} />
        <Route path="/tailor-resume" element={<ResumeTailorForm />} />
      </Route>
    </Routes>
  );
}