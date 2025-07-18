import { Routes, Route } from 'react-router-dom';

import ResumeTailorForm from '../components/ResumeTailorForm/ResumeTailorForm';
import LoginButton from '../components/GoogleLoginButton/GoogleLoginButton';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginButton />} />
      <Route path="/" element={<ResumeTailorForm />} />
    </Routes>
  );
}