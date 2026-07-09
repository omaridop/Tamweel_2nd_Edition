import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';
import NotFoundPage from '../pages/NotFoundPage';
import ErrorBoundary from '../components/ui/ErrorBoundary';
import ChatBot from '../components/ui/ChatBot';

// User Portal Pages
import UserDashboard from '../features/dashboard/UserDashboard';
import DataLinkingPage from '../features/accounts-linking/DataLinkingPage';
import ScoreSimulator from '../features/dashboard/ScoreSimulator';
import DisputeResolutionPage from '../features/disputes/DisputeResolutionPage';

// Sponsor Portal Pages
import SponsorDashboard from '../features/dashboard/SponsorDashboard';

const AppRoutes = () => {
  return (
    <ErrorBoundary>
      <Routes>
        {/* Auth Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* User Portal Routes */}
        <Route path="/dashboard" element={<UserDashboard />} />
        <Route path="/dashboard/connections" element={<DataLinkingPage />} />
        <Route path="/dashboard/simulator" element={<ScoreSimulator />} />
        <Route path="/dashboard/disputes" element={<DisputeResolutionPage />} />

        {/* Admin Portal Routes */}
        <Route path="/admin" element={<SponsorDashboard />} />
        <Route path="/admin/kyc" element={<SponsorDashboard />} /> {/* Placeholder for now */}
        <Route path="/admin/risk" element={<SponsorDashboard />} /> {/* Placeholder for now */}

        {/* Redirects */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      <ChatBot />
    </ErrorBoundary>
  );
};

export default AppRoutes;
