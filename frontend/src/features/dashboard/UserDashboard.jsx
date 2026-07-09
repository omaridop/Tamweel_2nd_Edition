import React, { useEffect, useState, useMemo, useRef, useCallback } from 'react';
import MainLayout from '../../layouts/MainLayout';
import { TwinPanelLayout } from '../../components/TwinPanelLayout';

import CreditScoreGauge from './CreditScoreGauge';
import SpendingAnalytics from './SpendingAnalytics';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { Brain, TrendingUp, Wallet, ArrowUpRight, Info, Loader2, Lightbulb, ShieldAlert, Activity, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';
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

  const handleGeneratePlan = useCallback(async () => {
    if (!user?.email) return;
    setIsGeneratingPlan(true);
    try {
      const response = await scoringService.generateImprovementPlan(user.name, user.email);
      setImprovementPlan(response.plan);
    } catch {
      alert("Failed to generate plan.");
    } finally {
      setIsGeneratingPlan(false);
    }
  }, [user?.name, user?.email]);

  const effectRan = useRef(false);

  useEffect(() => {
    if (effectRan.current === true) return;
    
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
        const results = await scoringService.getUserResults(user.email);
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
      } catch {
        // Fall silent on error
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    return () => {
      effectRan.current = true;
    };
  }, [user?.name, currentDetailedAssessment]);

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

  const xaiFactors = useMemo(() => [
    { label: 'Income Stability', impact: breakdown.income_stability > 30 ? 'High' : 'Medium', value: (breakdown.income_stability / 40) * 100, color: 'bg-emerald-500' },
    { label: 'Bill Payment History', impact: breakdown.bill_history > 20 ? 'High' : 'Medium', value: (breakdown.bill_history / 30) * 100, color: 'bg-amber-500' },
    { label: 'Financial Health', impact: breakdown.financial_health > 20 ? 'High' : 'Medium', value: (breakdown.financial_health / 30) * 100, color: 'bg-indigo-500' },
    { label: 'Account Maturity', impact: 'Low', value: 20, color: 'bg-blue-500' },
  ], [breakdown.income_stability, breakdown.bill_history, breakdown.financial_health]);

  // Dynamic Insights
  const allInsights = useMemo(() => {
    const strengths = assessment?.key_strengths?.map(s => ({ title: s, type: 'positive' })) || [];
    const risks = assessment?.key_risks?.map(r => ({ title: r, type: 'negative' })) || [];
    return [...strengths, ...risks];
  }, [assessment?.key_strengths, assessment?.key_risks]);

  if (loading) {
    return (
      <MainLayout>
        <div className="w-full h-[calc(100vh-8rem)] flex flex-col lg:flex-row gap-6 p-4">
          <div className="w-full lg:w-3/5 xl:w-2/3 space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="bg-slate-100 animate-pulse h-80 rounded-3xl"></div>
              <div className="lg:col-span-2 bg-slate-100 animate-pulse h-80 rounded-3xl"></div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map(i => <div key={i} className="bg-slate-100 animate-pulse h-28 rounded-2xl"></div>)}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-slate-100 animate-pulse h-96 rounded-3xl"></div>
              <div className="bg-slate-100 animate-pulse h-96 rounded-3xl"></div>
            </div>
          </div>
          <div className="w-full lg:w-2/5 xl:w-1/3 bg-slate-100 animate-pulse h-[600px] lg:h-full rounded-3xl"></div>
        </div>
      </MainLayout>
    );
  }

  if (!assessment) {
    return (
      <MainLayout>
        <TwinPanelLayout 
          leftPanel={
            <div className="flex flex-col items-center justify-center min-h-[600px] text-center p-8 bg-white rounded-3xl border border-slate-100 shadow-sm">
              <ShieldAlert className="w-16 h-16 text-slate-300 mb-6" />
              <h2 className="text-2xl font-bold text-slate-800 mb-2">No Financial Profile Found</h2>
              <p className="text-slate-500 max-w-md mb-8 leading-relaxed">
                We couldn't find a recent financial assessment for your account. Please connect your accounts or request a new assessment to see your AI credit score and insights.
              </p>
              <Button variant="primary" onClick={() => window.location.href = '/dashboard/connections'}>
                Connect Accounts
              </Button>
            </div>
          }
        />
      </MainLayout>
    );
  }

  // Mock data for the cash flow chart
  
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
  };

  return (
    <MainLayout>
      <TwinPanelLayout 
        leftPanel={
          <motion.div 
            variants={containerVariants} 
            initial="hidden" 
            animate="show" 
            className="space-y-8 w-full"
          >
        
        {/* Top Section: Score & Trend */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Gauge Card */}
          <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100 flex flex-col items-center" aria-label="Credit Score Gauge" tabIndex="0">
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
          <div className="lg:col-span-2 bg-white p-8 rounded-3xl shadow-soft border border-slate-100" aria-label="Score History Chart" tabIndex="0">
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
        </motion.div>
        {/* AI Reason Banner (Dynamic) */}
        {reason && (
          <motion.div variants={itemVariants} className="bg-indigo-600 rounded-3xl p-8 text-white relative overflow-hidden shadow-xl shadow-indigo-100">
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
          </motion.div>
        )}

        {/* High Level Metrics */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
           <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow group" aria-label="Limit Approved Metric" tabIndex="0">
              <div className="flex items-center gap-2 mb-2">
                <Wallet className="w-4 h-4 text-slate-400 group-hover:text-indigo-500 transition-colors" />
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Limit Approved</p>
              </div>
              <p className="text-2xl font-black text-slate-900">{approvedAmount} <span className="text-sm text-slate-400 font-medium">JOD</span></p>
           </div>
           <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow group" aria-label="Risk Assessment Metric" tabIndex="0">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-4 h-4 text-slate-400 group-hover:text-amber-500 transition-colors" />
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Risk Assessment</p>
              </div>
              <p className="text-2xl font-black text-slate-900">{riskLevel}</p>
           </div>
           <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow group" aria-label="Loan Status Metric" tabIndex="0">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-4 h-4 text-slate-400 group-hover:text-emerald-500 transition-colors" />
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Loan Status</p>
              </div>
              <p className="text-2xl font-black text-emerald-600">
                 {approvedAmount > 0 ? "Ready to Apply" : "Requires Improvement"}
              </p>
           </div>
        </motion.div>

        {/* Middle Section: AI Insights & XAI */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* XAI: Why this score? */}
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100" aria-label="Score Breakdown (XAI)" tabIndex="0">
            <div className="flex justify-between items-start mb-8">
              <h3 className="font-bold text-slate-900 flex items-center">
                <Brain className="w-5 h-5 mr-2 text-indigo-500" />
                Score Breakdown (XAI)
              </h3>
              <div className="flex gap-2">
                <span className="text-[10px] font-bold px-2 py-1 bg-slate-100 text-slate-600 rounded-lg uppercase tracking-wider">
                  Risk: {riskLevel}
                </span>
                <span className="text-[10px] font-bold px-2 py-1 bg-indigo-50 text-indigo-600 rounded-lg uppercase tracking-wider">
                  HIGH CONFIDENCE
                </span>
              </div>
            </div>
            
            <div className="space-y-6">
              {xaiFactors.map((factor) => {
                // Determine blocks out of 20 total blocks
                const totalBlocks = 20;
                const activeBlocks = Math.round((factor.value / 100) * totalBlocks);
                
                return (
                  <div key={factor.label} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-semibold text-slate-700">{factor.label}</span>
                      <span className="font-mono text-xs font-bold" style={{ color: factor.color.replace('bg-', 'text-').replace('-500', '-600') }}>
                        {factor.impact === 'High' && factor.value > 50 ? '+' : (factor.impact === 'Low' ? '-' : '')}{Math.round(factor.value / 3)}
                      </span>
                    </div>
                    <div className="flex gap-0.5 w-full h-3">
                      {Array.from({ length: totalBlocks }).map((_, i) => (
                        <div 
                          key={i} 
                          className={twMerge(
                            "flex-1 rounded-[1px] transition-colors",
                            i < activeBlocks ? factor.color : "bg-slate-100"
                          )}
                        />
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* AI Behavioral Insights & Improvement Tips */}
          <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm relative">
             <div className="flex justify-between items-start mb-6">
               <h3 className="font-bold text-slate-900 flex items-center">
                  <Lightbulb className="w-5 h-5 mr-2 text-amber-500" />
                  AI Intelligence Insights
               </h3>
               <span className="text-[10px] text-slate-400 font-medium bg-slate-50 px-2 py-1 rounded border border-slate-100">
                 {new Date().toLocaleDateString()}
               </span>
             </div>
             
             <div className="space-y-5">
                {allInsights.length > 0 ? allInsights.map((insight, idx) => (
                   <div key={idx} className="flex flex-col gap-3 p-5 bg-slate-50 hover:bg-slate-100/50 transition-colors rounded-2xl border border-slate-200/60">
                      <div className="flex items-start gap-3">
                        <div className={twMerge(
                          "shrink-0 w-8 h-8 rounded-lg flex items-center justify-center mt-0.5",
                          insight.type === 'positive' ? "bg-emerald-100 text-emerald-600" : "bg-rose-100 text-rose-600"
                        )}>
                           {insight.type === 'positive' ? <ArrowUpRight className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5" />}
                        </div>
                        <div>
                           <p className="text-[13px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                             {insight.type === 'positive' ? 'Positive Pattern' : 'Risk Factor'}
                           </p>
                           <p className="text-sm font-semibold text-slate-800 leading-snug">{insight.title}</p>
                           <p className="text-[13px] text-slate-600 mt-2 leading-relaxed">
                              {insight.type === 'positive' 
                                ? "This behavior indicates strong financial health and positively contributed to your underwriting limit." 
                                : "This metric flagged a potential underwriting risk. Addressing this could improve your credit tier."}
                           </p>
                        </div>
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
        </motion.div>

        {/* Bottom Section: Transaction Analytics */}
        <motion.div variants={itemVariants}>
          <SpendingAnalytics userEmail={user?.email} />
        </motion.div>
        </motion.div>
        }
      />
    </MainLayout>
  );
};

export default UserDashboard;
