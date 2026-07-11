import { useState, useEffect, useCallback } from 'react';
import { fetchWithAuth } from '../../services/api';
import useAuthStore from '../../store/useAuthStore';
import { AlertCircle, CheckCircle, Lightbulb, Search, Loader2 } from 'lucide-react';
import Button from '../ui/Button';

const AIInsightsCard = () => {
  const { user } = useAuthStore();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInsights = async () => {
      if (!user?.email) {
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        // User email is in the path for convention, but the backend extracts actual user from JWT
        const response = await fetchWithAuth(`/insights/${encodeURIComponent(user.email)}`);
        setData(response);
      } catch (err) {
        setError(err.message || 'Failed to fetch insights');
      } finally {
        setLoading(false);
      }
    };
    
    fetchInsights();
  }, [user]);

  const handleOpenChat = useCallback(() => {
    window.dispatchEvent(new CustomEvent('open-chat'));
    window.dispatchEvent(new CustomEvent('send-chat-message', {
      detail: { message: 'Give me a full financial health review' }
    }));
  }, []);

  if (loading) {
    return (
      <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-soft flex items-center justify-center h-48 mt-8">
        <Loader2 className="w-8 h-8 animate-spin text-accent" />
      </div>
    );
  }

  // Gracefully handle missing data or empty intelligence
  if (error || !data || !data.alerts || !data.strengths || !data.credit_improvement_tips || 
     (data.alerts.length === 0 && data.strengths.length === 0 && data.credit_improvement_tips.length === 0)) {
    return (
      <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-soft flex flex-col items-center text-center mt-8">
        <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
          <Search className="w-8 h-8 text-slate-300" />
        </div>
        <h3 className="text-lg font-bold text-primary mb-2">Connect your wallet to get personalized insights</h3>
        <p className="text-slate-500 max-w-md">
          We need transaction data to generate your personalized AI financial insights. Link your accounts to get started.
        </p>
      </div>
    );
  }

  const topAlert = data.alerts?.[0];
  const topStrength = data.strengths?.[0];
  const topTip = data.credit_improvement_tips?.[0];

  return (
    <div className="bg-white p-6 md:p-8 rounded-2xl border border-slate-100 shadow-lg relative overflow-hidden mt-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-primary">Proactive AI Insights</h2>
          <p className="text-sm text-slate-500 mt-1">Based on your recent transaction activity</p>
        </div>
        <Button onClick={handleOpenChat} variant="accent" className="hidden md:flex">
          See full analysis
        </Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 md:mb-0">
        {topAlert && (
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-100">
            <div className="flex items-center gap-2 mb-2 text-amber-600 font-bold">
              <AlertCircle className="w-5 h-5" />
              <span>Priority Alert</span>
            </div>
            <p className="text-amber-800 text-sm font-medium leading-relaxed">{topAlert}</p>
          </div>
        )}
        
        {topStrength && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-100">
            <div className="flex items-center gap-2 mb-2 text-emerald-600 font-bold">
              <CheckCircle className="w-5 h-5" />
              <span>Top Strength</span>
            </div>
            <p className="text-emerald-800 text-sm font-medium leading-relaxed">{topStrength}</p>
          </div>
        )}
        
        {topTip && (
          <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-100">
            <div className="flex items-center gap-2 mb-2 text-indigo-600 font-bold">
              <Lightbulb className="w-5 h-5" />
              <span>Credit Tip</span>
            </div>
            <p className="text-indigo-800 text-sm font-medium leading-relaxed">{topTip}</p>
          </div>
        )}
      </div>

      <Button onClick={handleOpenChat} variant="accent" className="w-full md:hidden mt-4">
        See full analysis
      </Button>
    </div>
  );
};

export default AIInsightsCard;
