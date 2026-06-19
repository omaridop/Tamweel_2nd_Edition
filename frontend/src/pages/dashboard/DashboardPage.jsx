import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../../components/ui/Button';

const DashboardPage = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-sm p-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Welcome, {user?.name || 'User'}!</h1>
            <p className="text-gray-600">This is your credit score overview.</p>
          </div>
          <Button variant="secondary" onClick={logout}>
            Logout
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-brand-primary p-6 rounded-xl text-white">
            <h3 className="text-sm opacity-80 mb-2">Current Score</h3>
            <p className="text-4xl font-bold">720</p>
            <p className="text-xs mt-2 text-blue-200">Excellent</p>
          </div>
          <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
            <h3 className="text-sm text-gray-500 mb-2">Analysis Status</h3>
            <p className="text-xl font-semibold text-gray-800">Processing AI Insights</p>
          </div>
          <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
            <h3 className="text-sm text-gray-500 mb-2">Next Update</h3>
            <p className="text-xl font-semibold text-gray-800">In 14 Days</p>
          </div>
        </div>

        <div className="mt-12 p-12 border-2 border-dashed border-gray-200 rounded-2xl flex items-center justify-center">
            <p className="text-gray-400">Phase 2: Detailed AI Credit Scoring Insights Coming Soon...</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
