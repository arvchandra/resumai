import { Routes, Route } from 'react-router-dom';

import ResumeTailorForm from '../components/ResumeTailorForm/ResumeTailorForm';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<ResumeTailorForm />} />
    </Routes>
  );
}