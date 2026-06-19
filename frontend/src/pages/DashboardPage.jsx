import React from 'react';
import MainLayout from '../layouts/MainLayout';
import { TrendingUp, Brain, Link as LinkIcon, AlertCircle } from 'lucide-react';
import Button from '../components/ui/Button';

const DashboardPage = () => {
  const stats = [
    { name: 'Credit Score', value: '742', change: '+12', icon: TrendingUp, color: 'text-accent' },
    { name: 'AI Confidence', value: '94%', change: 'Stable', icon: Brain, color: 'text-ai' },
    { name: 'Linked Accounts', value: '4', change: '2 Pending', icon: LinkIcon, color: 'text-blue-500' },
    { name: 'Active Disputes', value: '0', change: 'None', icon: AlertCircle, color: 'text-slate-400' },
  ];

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
        {/* Welcome Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-primary">Financial Overview</h1>
            <p className="text-slate-500 font-medium">Welcome back, Anas. Here's what's happening with your credit profile.</p>
          </div>
          <div className="flex gap-3">
             <Button variant="outline">Download Report</Button>
             <Button variant="accent">Update Data</Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => (
            <div key={stat.name} className="bg-white p-6 rounded-xl shadow-soft border border-slate-100 flex flex-col justify-between">
              <div className="flex justify-between items-start">
                <div className={`p-2 rounded-lg bg-slate-50 ${stat.color}`}>
                  <stat.icon className="w-5 h-5" />
                </div>
                <span className="text-xs font-bold text-emerald-500 px-2 py-1 bg-emerald-50 rounded-full">
                  {stat.change}
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-sm font-semibold text-slate-500">{stat.name}</h3>
                <p className="text-3xl font-bold text-primary mt-1">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* AI Insight Card (Glassmorphism) */}
        <div className="glass p-8 rounded-2xl border-indigo-100 shadow-lg shadow-indigo-50 relative overflow-hidden">
           <div className="absolute top-0 right-0 p-8 opacity-10">
              <Brain className="w-32 h-32 text-ai" />
           </div>
           <div className="relative z-10 max-w-2xl">
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-indigo-50 text-ai text-xs font-bold mb-4">
                 <Brain className="w-3 h-3 mr-2" />
                 AI Recommendation
              </div>
              <h2 className="text-xl font-bold text-primary mb-2">Boost your score by linking your utility bills</h2>
              <p className="text-slate-600 mb-6">
                Our AI model suggests that adding consistent utility payment history could potentially increase your score by <strong>15-25 points</strong> within the next 3 months.
              </p>
              <Button variant="ai">Link Utility Account</Button>
           </div>
        </div>

        {/* Placeholder for Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
           <div className="bg-white p-6 rounded-xl shadow-soft border border-slate-100 h-80 flex items-center justify-center text-slate-400 font-medium">
              Credit Score History Chart (Recharts)
           </div>
           <div className="bg-white p-6 rounded-xl shadow-soft border border-slate-100 h-80 flex items-center justify-center text-slate-400 font-medium">
              Spending Analysis by Category
           </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default DashboardPage;
