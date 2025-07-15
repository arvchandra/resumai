import { Routes, Route } from 'react-router-dom';

import ResumeTailorForm from '../components/ResumeTailorForm/ResumeTailorForm';
import LoginButton from '../components/Login/LoginButton';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LoginButton />} />
      <Route path="/tailor-resume" element={<ResumeTailorForm />} />
    </Routes>
  );
}