import React, { useState, useEffect } from 'react';
import MainLayout from '../../layouts/MainLayout';
import Button from '../../components/ui/Button';
import { Brain, Calculator, TrendingUp, AlertCircle, Info } from 'lucide-react';
import { twMerge } from 'tailwind-merge';

const ScoreSimulator = () => {
  const baseScore = 742;
  const [simulatedScore, setSimulatedScore] = useState(baseScore);
  const [actions, setActions] = useState({
    payBillsOnTime: false,
    increaseSpending: false,
    newLoan: false,
    payOffDebt: false,
  });

  useEffect(() => {
    let change = 0;
    if (actions.payBillsOnTime) change += 25;
    if (actions.increaseSpending) change -= 40;
    if (actions.newLoan) change -= 15;
    if (actions.payOffDebt) change += 35;
    
    setSimulatedScore(baseScore + change);
  }, [actions]);

  const toggleAction = (key) => {
    setActions(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-ai/10 rounded-lg">
            <Brain className="w-6 h-6 text-ai" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-primary">AI Score Simulator</h1>
            <p className="text-slate-500 text-sm">Predict how your financial decisions impact your creditworthiness.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Actions Panel */}
          <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100 space-y-6">
            <h3 className="font-bold text-primary flex items-center">
              <Calculator className="w-4 h-4 mr-2 text-slate-400" />
              Select Actions
            </h3>
            
            <div className="space-y-4">
              {[
                { key: 'payBillsOnTime', label: 'Pay all bills on time for 3 months', impact: '+25 pts', positive: true },
                { key: 'payOffDebt', label: 'Pay off 200 JOD of existing debt', impact: '+35 pts', positive: true },
                { key: 'increaseSpending', label: 'Increase monthly spending by 50%', impact: '-40 pts', positive: false },
                { key: 'newLoan', label: 'Take out a new micro-loan', impact: '-15 pts', positive: false },
              ].map((item) => (
                <button
                  key={item.key}
                  onClick={() => toggleAction(item.key)}
                  className={twMerge(
                    "w-full flex items-center justify-between p-4 rounded-2xl border transition-all duration-200",
                    actions[item.key] 
                      ? "border-accent bg-emerald-50 shadow-sm" 
                      : "border-slate-100 bg-slate-50 hover:bg-white hover:border-slate-200"
                  )}
                >
                  <span className={twMerge("font-medium text-sm", actions[item.key] ? "text-primary" : "text-slate-600")}>
                    {item.label}
                  </span>
                  <span className={twMerge(
                    "text-xs font-bold px-2 py-1 rounded-full",
                    item.positive ? "text-emerald-600 bg-emerald-100/50" : "text-red-600 bg-red-100/50"
                  )}>
                    {item.impact}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Result Panel */}
          <div className="bg-primary text-white p-8 rounded-3xl shadow-xl flex flex-col items-center justify-center relative overflow-hidden">
             <div className="relative z-10 text-center space-y-4">
                <p className="text-slate-300 font-bold uppercase tracking-widest text-xs">Simulated Score</p>
                <div className="text-7xl font-black text-white">{simulatedScore}</div>
                <div className="flex items-center justify-center gap-2">
                   <TrendingUp className={twMerge("w-5 h-5", simulatedScore >= baseScore ? "text-accent" : "text-red-400")} />
                   <span className={twMerge("font-bold", simulatedScore >= baseScore ? "text-accent" : "text-red-400")}>
                      {simulatedScore - baseScore >= 0 ? '+' : ''}{simulatedScore - baseScore} points change
                   </span>
                </div>
                <p className="text-xs text-slate-400 max-w-[200px] mx-auto pt-4 leading-relaxed">
                  *This is an AI prediction based on historical patterns. Actual results may vary.
                </p>
             </div>
             
             {/* Decorative AI Glow */}
             <div className="absolute inset-0 bg-gradient-to-br from-ai/20 to-transparent pointer-events-none"></div>
          </div>
        </div>

        {/* Insight Box */}
        <div className="glass p-6 rounded-2xl border-indigo-100 flex items-start gap-4">
           <Info className="text-ai w-6 h-6 mt-1" />
           <div>
              <h4 className="font-bold text-primary">AI Analysis of Selection</h4>
              <p className="text-sm text-slate-600 mt-1">
                Based on your current ZainCash patterns, paying off debt has the highest immediate impact because your 
                debt-to-income ratio is currently the primary factor limiting your score growth.
              </p>
           </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default ScoreSimulator;
