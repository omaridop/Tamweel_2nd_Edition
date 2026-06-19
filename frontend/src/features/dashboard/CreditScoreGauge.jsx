import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { twMerge } from 'tailwind-merge';

const CreditScoreGauge = ({ score }) => {
  const data = [
    { name: 'Score', value: score },
    { name: 'Remaining', value: 850 - score },
  ];

  const getColor = (s) => {
    if (s < 580) return '#EF4444'; // Poor
    if (s < 670) return '#F59E0B'; // Fair
    if (s < 740) return '#3B82F6'; // Good
    return '#10B981'; // Excellent
  };

  const getLabel = (s) => {
    if (s < 580) return 'Poor';
    if (s < 670) return 'Fair';
    if (s < 740) return 'Good';
    return 'Excellent';
  };

  return (
    <div className="relative w-full h-64 flex flex-col items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="80%"
            startAngle={180}
            endAngle={0}
            innerRadius={80}
            outerRadius={110}
            paddingAngle={0}
            dataKey="value"
            stroke="none"
          >
            <Cell fill={getColor(score)} />
            <Cell fill="#E2E8F0" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      
      <div className="absolute top-[55%] flex flex-col items-center">
        <span className="text-5xl font-black text-primary">{score}</span>
        <span className={twMerge("text-sm font-bold uppercase tracking-widest mt-1")} style={{ color: getColor(score) }}>
          {getLabel(score)}
        </span>
      </div>
      
      <div className="flex justify-between w-full max-w-[220px] text-[10px] font-bold text-slate-400 mt-[-20px]">
        <span>300</span>
        <span>850</span>
      </div>
    </div>
  );
};

export default CreditScoreGauge;
