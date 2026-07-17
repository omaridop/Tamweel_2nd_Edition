import { useState, useMemo } from 'react';
import MainLayout from '../../layouts/MainLayout';
import Button from '../../components/ui/Button';
import { Calculator, TrendingUp, TrendingDown, Info, Sliders, Sparkles, CreditCard } from 'lucide-react';
import { twMerge } from 'tailwind-merge';
import useAuthStore from '../../store/useAuthStore';

const ScoreSimulator = () => {
  const { detailedAssessment } = useAuthStore();
  
  // Use real score if available, otherwise fallback
  const baseScore = detailedAssessment?.credit_score || 640;
  
  const [sliders, setSliders] = useState({
    payDownDebt: 0, // 0 to 1000 JOD
    increaseCreditLimit: 0, // 0 to 5000 JOD
    newInquiries: 0, // 0 to 5 inquiries
  });

  const [activePlan, setActivePlan] = useState(null);

  // Recalculate score based on slider values directly during render
  let change = 0;
  
  // Paying down debt increases score (up to +45 points)
  if (sliders.payDownDebt > 0) {
    change += Math.floor((sliders.payDownDebt / 1000) * 45);
  }
  
  // Increasing limit lowers utilization, increasing score slightly (+15 points max)
  if (sliders.increaseCreditLimit > 0) {
    change += Math.floor((sliders.increaseCreditLimit / 5000) * 15);
  }

  // New inquiries lower score (-5 points each)
  if (sliders.newInquiries > 0) {
    change -= (sliders.newInquiries * 5);
  }
  
  const simulatedScore = baseScore + change;

  const handleSliderChange = (e, key) => {
    setActivePlan(null); // Reset smart plan if user manually adjusts
    setSliders(prev => ({ ...prev, [key]: Number(e.target.value) }));
  };

  const applySmartPlan = () => {
    setSliders({
      payDownDebt: 500,
      increaseCreditLimit: 1000,
      newInquiries: 0
    });
    setActivePlan("Optimal Debt-to-Limit Ratio Plan");
  };

  const scoreDiff = simulatedScore - baseScore;

  // ── Repayment Simulator ──────────────────────────────────────
  const approvedAmount = (detailedAssessment?.approved_amount_jod || baseScore * 8);

  const [repayment, setRepayment] = useState({
    amount: approvedAmount > 0 ? Math.min(approvedAmount, 5000) : 1000,
    rate: 8,      // annual % interest
    termMonths: 24,
  });

  const repayCalc = useMemo(() => {
    const { amount, rate, termMonths } = repayment;
    if (termMonths === 0 || rate === 0) {
      return {
        monthly: amount / (termMonths || 1),
        totalInterest: 0,
        totalRepayment: amount,
      };
    }
    const r = rate / 100 / 12; // monthly rate
    const n = termMonths;
    const monthly = (amount * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
    const totalRepayment = monthly * n;
    const totalInterest = totalRepayment - amount;
    return {
      monthly: Math.round(monthly * 100) / 100,
      totalInterest: Math.round(totalInterest * 100) / 100,
      totalRepayment: Math.round(totalRepayment * 100) / 100,
    };
  }, [repayment]);

  return (
    <MainLayout>
      <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-accent/10 rounded-lg">
              <Sliders className="w-6 h-6 text-accent" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-primary">Interactive Score Simulator</h1>
              <p className="text-slate-500 text-sm mt-1">Adjust the sliders to see how financial actions will impact your Tamweel AI score.</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Controls */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Simulation Sliders */}
            <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100">
              <h3 className="font-bold text-primary flex items-center mb-8">
                <Calculator className="w-4 h-4 mr-2 text-slate-400" />
                "What-If" Analysis
              </h3>
              
              <div className="space-y-8">
                {/* Slider 1 */}
                <div className="space-y-3">
                  <div className="flex justify-between items-end">
                    <div>
                      <label className="font-bold text-sm text-primary">Pay Down Debt</label>
                      <p className="text-xs text-slate-500">How much existing debt will you pay off?</p>
                    </div>
                    <span className="font-bold text-accent">{sliders.payDownDebt} JOD</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" max="1000" step="50"
                    value={sliders.payDownDebt}
                    onChange={(e) => handleSliderChange(e, 'payDownDebt')}
                    className="w-full accent-accent h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
                    aria-label="Pay Down Debt Amount"
                    aria-valuenow={sliders.payDownDebt}
                  />
                </div>

                {/* Slider 2 */}
                <div className="space-y-3">
                  <div className="flex justify-between items-end">
                    <div>
                      <label className="font-bold text-sm text-primary">Request Limit Increase</label>
                      <p className="text-xs text-slate-500">Lowers your credit utilization ratio.</p>
                    </div>
                    <span className="font-bold text-accent">{sliders.increaseCreditLimit} JOD</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" max="5000" step="100"
                    value={sliders.increaseCreditLimit}
                    onChange={(e) => handleSliderChange(e, 'increaseCreditLimit')}
                    className="w-full accent-accent h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
                    aria-label="Request Limit Increase Amount"
                    aria-valuenow={sliders.increaseCreditLimit}
                  />
                </div>

                {/* Slider 3 */}
                <div className="space-y-3">
                  <div className="flex justify-between items-end">
                    <div>
                      <label className="font-bold text-sm text-primary">New Credit Inquiries</label>
                      <p className="text-xs text-slate-500">Applying for new loans or cards.</p>
                    </div>
                    <span className="font-bold text-red-500">{sliders.newInquiries}</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" max="5" step="1"
                    value={sliders.newInquiries}
                    onChange={(e) => handleSliderChange(e, 'newInquiries')}
                    className="w-full accent-red-500 h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2"
                    aria-label="New Credit Inquiries"
                    aria-valuenow={sliders.newInquiries}
                  />
                </div>
              </div>
            </div>

            {/* Smart Action Plans */}
            <div className="bg-gradient-to-r from-emerald-50 to-teal-50 p-6 rounded-2xl border border-emerald-100 relative overflow-hidden">
              <div className="relative z-10 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <div className="inline-flex items-center px-2 py-1 bg-emerald-200/50 text-emerald-800 rounded text-[10px] font-bold uppercase mb-2">
                    <Sparkles className="w-3 h-3 mr-1" />
                    AI Recommendation
                  </div>
                  <h4 className="font-bold text-emerald-950">Smart Action Plan</h4>
                  <p className="text-sm text-emerald-800/80 mt-1">Let our AI find the fastest path to boost your score by 25+ points.</p>
                </div>
                <Button variant="primary" className="bg-emerald-600 hover:bg-emerald-700 border-emerald-600 text-white shadow-emerald-600/20 whitespace-nowrap" onClick={applySmartPlan}>
                  Apply Optimal Plan
                </Button>
              </div>
            </div>
          </div>

          {/* Result Panel */}
          <div className="bg-primary text-white p-8 rounded-3xl shadow-xl flex flex-col items-center justify-start relative overflow-hidden h-full min-h-[400px]">
             <div className="relative z-10 w-full flex flex-col items-center h-full">
                <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-8">Simulated AI Score</p>
                
                {/* Dynamic Score Display */}
                <div className="relative flex items-center justify-center w-48 h-48 mb-8">
                  <svg className="absolute inset-0 w-full h-full -rotate-90 transform">
                    <circle 
                      cx="96" cy="96" r="88" 
                      className="stroke-white/10" strokeWidth="12" fill="none" 
                    />
                    <circle 
                      cx="96" cy="96" r="88" 
                      className={twMerge("transition-all duration-1000 ease-out", scoreDiff >= 0 ? "stroke-accent" : "stroke-red-500")}
                      strokeWidth="12" fill="none" 
                      strokeDasharray="552.9" 
                      strokeDashoffset={552.9 - (552.9 * Math.min(simulatedScore, 1000)) / 1000}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="text-center" aria-live="polite" aria-atomic="true">
                    <div className="text-5xl font-black text-white">{simulatedScore}</div>
                    <div className="text-xs text-slate-400 font-medium mt-1">out of 1000</div>
                  </div>
                </div>

                <div className={twMerge(
                  "flex items-center justify-center gap-2 px-4 py-2 rounded-full border",
                  scoreDiff >= 0 ? "bg-emerald-500/10 border-emerald-500/20 text-accent" : "bg-red-500/10 border-red-500/20 text-red-400"
                )}>
                   {scoreDiff >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
                   <span className="font-bold">
                      {scoreDiff >= 0 ? '+' : ''}{scoreDiff} points
                   </span>
                </div>

                {activePlan && (
                  <div className="mt-8 text-center animate-in slide-in-from-bottom-2">
                    <p className="text-xs text-emerald-400 font-bold uppercase">Active Plan</p>
                    <p className="text-sm font-medium mt-1">{activePlan}</p>
                  </div>
                )}
             </div>
             
             {/* Decorative Background */}
             <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 blur-3xl -mr-20 -mt-20"></div>
          </div>
        </div>

        {/* Insight Box */}
        <div className="glass p-6 rounded-2xl border-indigo-100 flex items-start gap-4 shadow-sm">
           <div className="p-2 bg-indigo-50 rounded-lg">
             <Info className="text-indigo-500 w-5 h-5" />
           </div>
           <div>
              <h4 className="font-bold text-primary">Why this matters</h4>
              <p className="text-sm text-slate-600 mt-1">
                Your credit score is highly sensitive to your <strong>Credit Utilization Ratio</strong>. By paying down debt while simultaneously increasing your total available credit limit, you can drastically lower your utilization ratio, resulting in the largest possible score boost.
              </p>
           </div>
        </div>
       </div>

        {/* ── Repayment Simulator ─────────────────────────────── */}
        <div className="bg-white rounded-3xl shadow-soft border border-slate-100 p-8 space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-emerald-50 rounded-lg">
              <CreditCard className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-primary">Repayment Simulator</h2>
              <p className="text-sm text-slate-500">Adjust loan amount, interest rate, and term to see your monthly payment.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Sliders */}
            <div className="lg:col-span-2 space-y-6">
              {/* Loan Amount */}
              <div className="space-y-2">
                <div className="flex justify-between">
                  <label className="font-bold text-sm text-primary">Loan Amount</label>
                  <span className="font-bold text-emerald-600">{repayment.amount.toLocaleString()} JOD</span>
                </div>
                <input
                  type="range" min="100" max="10000" step="100"
                  value={repayment.amount}
                  onChange={e => setRepayment(p => ({ ...p, amount: Number(e.target.value) }))}
                  className="w-full accent-emerald-500 h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
                  aria-label="Loan Amount"
                />
              </div>

              {/* Interest Rate */}
              <div className="space-y-2">
                <div className="flex justify-between">
                  <label className="font-bold text-sm text-primary">Annual Interest Rate</label>
                  <span className="font-bold text-emerald-600">{repayment.rate}%</span>
                </div>
                <input
                  type="range" min="1" max="30" step="0.5"
                  value={repayment.rate}
                  onChange={e => setRepayment(p => ({ ...p, rate: Number(e.target.value) }))}
                  className="w-full accent-emerald-500 h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
                  aria-label="Annual Interest Rate"
                />
              </div>

              {/* Loan Term */}
              <div className="space-y-2">
                <div className="flex justify-between">
                  <label className="font-bold text-sm text-primary">Loan Term</label>
                  <span className="font-bold text-emerald-600">{repayment.termMonths} months</span>
                </div>
                <input
                  type="range" min="3" max="60" step="3"
                  value={repayment.termMonths}
                  onChange={e => setRepayment(p => ({ ...p, termMonths: Number(e.target.value) }))}
                  className="w-full accent-emerald-500 h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
                  aria-label="Loan Term in Months"
                />
              </div>
            </div>

            {/* Results Panel */}
            <div className="bg-gradient-to-br from-emerald-600 to-teal-700 text-white rounded-2xl p-6 flex flex-col justify-center gap-5 shadow-xl shadow-emerald-900/20">
              <div>
                <p className="text-emerald-200 text-xs font-bold uppercase tracking-widest mb-1">Monthly Payment</p>
                <p className="text-4xl font-black">{repayCalc.monthly.toLocaleString()} <span className="text-lg font-medium text-emerald-200">JOD</span></p>
              </div>
              <div className="border-t border-white/20 pt-4 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-emerald-200">Principal</span>
                  <span className="font-bold">{repayment.amount.toLocaleString()} JOD</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-emerald-200">Total Interest</span>
                  <span className="font-bold">{repayCalc.totalInterest.toLocaleString()} JOD</span>
                </div>
                <div className="flex justify-between text-sm border-t border-white/20 pt-3">
                  <span className="text-emerald-100 font-bold">Total Repayment</span>
                  <span className="font-black text-white">{repayCalc.totalRepayment.toLocaleString()} JOD</span>
                </div>
              </div>
            </div>
          </div>
        </div>
    </MainLayout>
  );
};

export default ScoreSimulator;
