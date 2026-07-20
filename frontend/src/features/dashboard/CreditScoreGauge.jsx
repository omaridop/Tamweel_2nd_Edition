import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { twMerge } from 'tailwind-merge';

const CreditScoreGauge = ({ score }) => {
  const data = [
    { name: 'Score', value: score },
    { name: 'Remaining', value: 100 - score },
  ];

  const getColor = (s) => {
    if (s < 20) return '#EF4444'; // Very Poor
    if (s < 40) return '#F87171'; // Poor
    if (s < 60) return '#F59E0B'; // Fair
    if (s < 80) return '#3B82F6'; // Good
    return '#10B981'; // Excellent
  };

  const getLabel = (s) => {
    if (s < 20) return 'Very Poor';
    if (s < 40) return 'Poor';
    if (s < 60) return 'Fair';
    if (s < 80) return 'Good';
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
            innerRadius={85}
            outerRadius={115}
            paddingAngle={0}
            dataKey="value"
            stroke="none"
          >
            <Cell fill={getColor(score)} className="transition-all duration-1000 ease-out" />
            <Cell fill="#F1F5F9" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      
      <div className="absolute top-[52%] flex flex-col items-center">
        <span className="text-6xl font-black text-slate-900 tracking-tighter">{score}</span>
        <span className={twMerge("text-xs font-bold uppercase tracking-widest mt-2")} style={{ color: getColor(score) }}>
          {getLabel(score)}
        </span>
      </div>
      
      <div className="flex justify-between w-full max-w-[240px] text-[11px] font-bold text-slate-400 mt-[-15px]">
        <span>300</span>
        <span>850</span>
      </div>
    </div>
  );
};

export default CreditScoreGauge;
