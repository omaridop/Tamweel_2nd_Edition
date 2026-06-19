import React, { useEffect, useState } from 'react';
import MainLayout from '../../layouts/MainLayout';
import CreditScoreGauge from './CreditScoreGauge';
import SpendingAnalytics from './SpendingAnalytics';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { Brain, TrendingUp, Wallet, ArrowUpRight, ArrowDownRight, Info, Loader2, Lightbulb, ShieldAlert } from 'lucide-react';
import Button from '../../components/ui/Button';
import { twMerge } from 'tailwind-merge';
import { scoringService } from '../../services/api';
import useAuthStore from '../../store/useAuthStore';

const UserDashboard = () => {
  const { user, currentDetailedAssessment } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [assessment, setLatestAssessment] = useState(null);
  const [history, setHistory] = useState([]);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
  const [improvementPlan, setImprovementPlan] = useState("");

  const handleGeneratePlan = async () => {
    if (!user?.email) return;
    setIsGeneratingPlan(true);
    try {
      const response = await scoringService.generateImprovementPlan(user.name, user.email);
      setImprovementPlan(response.plan);
    } catch (error) {
      alert("Failed to generate plan.");
    } finally {
      setIsGeneratingPlan(false);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      // If we have a fresh assessment from the session, use it
      if (currentDetailedAssessment) {
        setLatestAssessment(currentDetailedAssessment);
        setLoading(false);
      }

      if (!user?.name) {
        if (!currentDetailedAssessment) setLoading(false);
        return;
      }
      try {
        // Fetch historical assessments for the user
        const results = await scoringService.getUserResults(user.name);
        if (results && results.length > 0) {
          // Sort by date and get latest
          const sorted = results.sort((a, b) => new Date(b.generated_at) - new Date(a.generated_at));
          
          if (!currentDetailedAssessment) {
            setLatestAssessment(sorted[0]);
          }
          
          // Format history for chart (last 6 entries)
          const chartData = sorted.slice(0, 6).reverse().map(item => ({
            month: new Date(item.generated_at).toLocaleDateString('en-US', { month: 'short' }),
            score: item.credit_score
          }));
          setHistory(chartData);
        } else {
          // Fallback history for new users or when Supabase is empty
          const fallbackScore = currentDetailedAssessment?.credit_score || currentDetailedAssessment?.final_score || 70;
          setHistory([
            { month: 'Jan', score: 45 },
            { month: 'Feb', score: 52 },
            { month: 'Mar', score: 48 },
            { month: 'Apr', score: 60 },
            { month: 'May', score: 65 },
            { month: 'Jun', score: fallbackScore },
          ]);
        }
      } catch (error) {
        console.error("Failed to fetch user dashboard data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user?.name, currentDetailedAssessment]);

  if (loading) {
    return (
      <MainLayout>
        <div className="h-[60vh] flex flex-col items-center justify-center text-slate-400">
           <Loader2 className="w-10 h-10 animate-spin mb-4 text-accent" />
           <p className="font-bold">Syncing AI Credit Insights...</p>
        </div>
      </MainLayout>
    );
  }

  // Use assessment data if available, otherwise fallback to defaults
  const currentScore = Math.round(assessment?.credit_score || assessment?.final_score || 0);
  const approvedAmount = assessment?.approved_amount_jod || 0;
  const riskLevel = assessment?.risk_level || "Calculating...";
  const reason = assessment?.reason || "";
  
  // Dynamic Score Breakdown
  const breakdown = assessment?.score_breakdown || {
    income_stability: 30,
    bill_history: 20,
    financial_health: 20
  };

  const xaiFactors = [
    { label: 'Income Stability', impact: breakdown.income_stability > 30 ? 'High' : 'Medium', value: (breakdown.income_stability / 40) * 100, color: 'bg-emerald-500' },
    { label: 'Bill Payment History', impact: breakdown.bill_history > 20 ? 'High' : 'Medium', value: (breakdown.bill_history / 30) * 100, color: 'bg-amber-500' },
    { label: 'Financial Health', impact: breakdown.financial_health > 20 ? 'High' : 'Medium', value: (breakdown.financial_health / 30) * 100, color: 'bg-indigo-500' },
    { label: 'Account Maturity', impact: 'Low', value: 20, color: 'bg-blue-500' },
  ];

  // Dynamic Insights
  const strengths = assessment?.key_strengths?.map(s => ({ title: s, type: 'positive' })) || [];
  const risks = assessment?.key_risks?.map(r => ({ title: r, type: 'negative' })) || [];
  const allInsights = [...strengths, ...risks];

  // Mock data for the cash flow chart
  const cashFlowData = [
    { day: 'Mon', income: 45, expenses: 32 },
    { day: 'Tue', income: 52, expenses: 40 },
    { day: 'Wed', income: 48, expenses: 38 },
    { day: 'Thu', income: 70, expenses: 45 },
    { day: 'Fri', income: 61, expenses: 50 },
    { day: 'Sat', income: 35, expenses: 25 },
    { day: 'Sun', income: 40, expenses: 20 },
  ];

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-700">
        
        {/* Top Section: Score & Trend */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Gauge Card */}
          <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100 flex flex-col items-center">
            <div className="w-full flex justify-between items-center mb-4">
              <h3 className="font-bold text-primary">Your AI Credit Score</h3>
              <Info className="w-4 h-4 text-slate-400 cursor-help" />
            </div>
            <CreditScoreGauge score={currentScore} />
            <div className="mt-4 text-center">
              <p className="text-xs text-slate-400 font-medium">
                Last updated: {assessment ? new Date(assessment.generated_at || assessment.timestamp).toLocaleDateString() : 'N/A'}
              </p>
              <Button variant="ghost" className="text-accent text-xs font-bold mt-2">See what changed</Button>
            </div>
          </div>

          {/* Trend Chart Card */}
          <div className="lg:col-span-2 bg-white p-8 rounded-3xl shadow-soft border border-slate-100">
            <div className="flex justify-between items-center mb-8">
              <div>
                <h3 className="font-bold text-primary">Score History</h3>
                <p className="text-xs text-slate-400 font-medium">Your progress over the last assessments</p>
              </div>
              <div className="flex items-center text-emerald-500 font-bold bg-emerald-50 px-3 py-1 rounded-full text-sm">
                <TrendingUp className="w-4 h-4 mr-1" />
                Live Sync
              </div>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={history.length > 0 ? history : [{month: 'N/A', score: 0}]}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#94A3B8', fontSize: 12}} dy={10} />
                  <YAxis hide domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#10B981" 
                    strokeWidth={4} 
                    dot={{ r: 6, fill: '#10B981', strokeWidth: 3, stroke: '#fff' }}
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* AI Reason Banner (Dynamic) */}
        {reason && (
          <div className="bg-indigo-600 rounded-3xl p-8 text-white relative overflow-hidden shadow-xl shadow-indigo-100">
             <div className="relative z-10">
                <div className="flex items-center gap-2 mb-4">
                   <div className="p-2 bg-white/20 rounded-lg">
                      <Brain className="w-5 h-5 text-white" />
                   </div>
                   <span className="font-bold text-sm uppercase tracking-widest opacity-80">AI Assessment Conclusion</span>
                </div>
                <p className="text-2xl font-bold leading-relaxed max-w-4xl" dir="rtl">
                   "{reason}"
                </p>
             </div>
             {/* Decorative Background */}
             <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
          </div>
        )}

        {/* High Level Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
           <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-soft">
              <p className="text-xs font-bold text-slate-400 uppercase">Limit Approved</p>
              <p className="text-2xl font-black text-primary mt-1">{approvedAmount} JOD</p>
           </div>
           <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-soft">
              <p className="text-xs font-bold text-slate-400 uppercase">Risk Assessment</p>
              <p className="text-2xl font-black text-primary mt-1">{riskLevel}</p>
           </div>
           <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-soft">
              <p className="text-xs font-bold text-slate-400 uppercase">Loan Status</p>
              <p className="text-2xl font-black text-emerald-500 mt-1">
                 {approvedAmount > 0 ? "Ready to Apply" : "Requires Improvement"}
              </p>
           </div>
        </div>

        {/* Middle Section: AI Insights & XAI */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* XAI: Why this score? */}
          <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100">
            <h3 className="font-bold text-primary mb-6 flex items-center">
              <Brain className="w-5 h-5 mr-2 text-ai" />
              Score Breakdown (XAI)
            </h3>
            <div className="space-y-6">
              {xaiFactors.map((factor) => (
                <div key={factor.label} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-bold text-slate-700">{factor.label}</span>
                    <span className="text-slate-400">Impact: <span className="font-bold text-primary">{factor.impact}</span></span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div className={twMerge("h-full rounded-full transition-all duration-1000", factor.color)} style={{ width: `${factor.value}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Behavioral Insights & Improvement Tips */}
          <div className="glass p-8 rounded-3xl border-indigo-100 shadow-lg shadow-indigo-50 relative">
             <h3 className="font-bold text-primary mb-6 flex items-center">
                <Lightbulb className="w-5 h-5 mr-2 text-amber-500" />
                AI Behavioral Insights & Tips
             </h3>
             <div className="space-y-4">
                {allInsights.length > 0 ? allInsights.map((insight, idx) => (
                   <div key={idx} className="flex gap-4 p-4 bg-white/50 rounded-2xl border border-white">
                      <div className={twMerge(
                        "shrink-0 w-10 h-10 rounded-xl flex items-center justify-center",
                        insight.type === 'positive' ? "bg-emerald-100 text-emerald-600" : "bg-amber-100 text-amber-600"
                      )}>
                         {insight.type === 'positive' ? <ArrowUpRight className="w-6 h-6" /> : <ShieldAlert className="w-6 h-6" />}
                      </div>
                      <div>
                         <p className="text-sm font-bold text-primary">{insight.title}</p>
                         <p className="text-xs text-slate-600 mt-1">
                            {insight.type === 'positive' ? "This factor boosted your score." : "Improving this will increase your score."}
                         </p>
                      </div>
                   </div>
                )) : (
                  <div className="text-center py-8 text-slate-400 font-medium">
                     No insights available yet.
                  </div>
                )}
                <Button 
                   variant="ai" 
                   className="w-full mt-4" 
                   onClick={handleGeneratePlan}
                   disabled={isGeneratingPlan}
                >
                   {isGeneratingPlan ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : "Generate Improvement Plan"}
                </Button>
                
                {improvementPlan && (
                   <div className="mt-6 p-5 bg-indigo-50 border border-indigo-100 rounded-2xl animate-in fade-in slide-in-from-top-4">
                      <h4 className="font-bold text-indigo-900 mb-3 flex items-center">
                         <Brain className="w-4 h-4 mr-2" />
                         Your Personalized Action Plan
                      </h4>
                      <div className="text-sm text-indigo-800 space-y-2 whitespace-pre-wrap leading-relaxed" dir="rtl">
                         {improvementPlan}
                      </div>
                   </div>
                )}
             </div>
          </div>
        </div>

        {/* Bottom Section: Transaction Analytics */}
        <SpendingAnalytics userEmail={user?.email} />
      </div>
    </MainLayout>
  );
};

export default UserDashboard;
