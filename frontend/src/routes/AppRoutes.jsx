import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';

// User Portal Pages
import UserDashboard from '../features/dashboard/UserDashboard';
import DataLinkingPage from '../features/accounts-linking/DataLinkingPage';
import ScoreSimulator from '../features/dashboard/ScoreSimulator';
import DisputeResolutionPage from '../features/disputes/DisputeResolutionPage';

// Sponsor Portal Pages
import SponsorDashboard from '../features/dashboard/SponsorDashboard';

const AppRoutes = () => {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* User Portal Routes */}
      <Route path="/user">
        <Route path="dashboard" element={<UserDashboard />} />
        <Route path="connections" element={<DataLinkingPage />} />
        <Route path="simulator" element={<ScoreSimulator />} />
        <Route path="disputes" element={<DisputeResolutionPage />} />
      </Route>

      {/* Sponsor Portal Routes */}
      <Route path="/sponsor">
        <Route path="dashboard" element={<SponsorDashboard />} />
      </Route>

      {/* Redirects */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/user/dashboard" replace />} />
    </Routes>
  );
};

export default AppRoutes;
