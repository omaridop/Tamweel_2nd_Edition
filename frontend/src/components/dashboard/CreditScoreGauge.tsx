import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export const CreditScoreGauge: React.FC<{ score: number }> = ({ score }) => {
  const [currentScore, setCurrentScore] = useState(0);
  
  useEffect(() => {
    const duration = 1500;
    const steps = 60;
    const stepTime = duration / steps;
    const increment = score / steps;
    
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setCurrentScore(score);
        clearInterval(timer);
      } else {
        setCurrentScore(Math.floor(current));
      }
    }, stepTime);
    
    return () => clearInterval(timer);
  }, [score]);

  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (score / 1000) * circumference;

  return (
    <div className="relative flex items-center justify-center w-56 h-56 bg-brand-dark rounded-full shadow-2xl border border-brand-accent/20">
      <svg className="absolute w-full h-full transform -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" className="stroke-brand-base fill-none" strokeWidth="8" />
        <motion.circle
          cx="50" cy="50" r="45"
          className="stroke-brand-xai fill-none"
          strokeWidth="8"
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          style={{ strokeDasharray: circumference }}
        />
      </svg>
      <div className="flex flex-col items-center z-10">
        <span className="text-5xl font-bold text-white tracking-tighter">{currentScore}</span>
        <span className="text-xs text-brand-accent uppercase font-semibold mt-1 tracking-widest">Alt Score</span>
      </div>
    </div>
  );
};
