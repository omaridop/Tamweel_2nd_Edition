import React from 'react';
import { motion } from 'framer-motion';

const cohortData = [
  { month: 'Jan', size: 1200, m1: 98, m2: 85, m3: 75, m4: 60, m5: 55, m6: 50 },
  { month: 'Feb', size: 1450, m1: 99, m2: 88, m3: 79, m4: 65, m5: 58, m6: null },
  { month: 'Mar', size: 1100, m1: 97, m2: 82, m3: 71, m4: 58, m5: null, m6: null },
  { month: 'Apr', size: 1600, m1: 99, m2: 90, m3: 82, m4: null, m5: null, m6: null },
  { month: 'May', size: 1800, m1: 98, m2: 89, m3: null, m4: null, m5: null, m6: null },
  { month: 'Jun', size: 2100, m1: 99, m2: null, m3: null, m4: null, m5: null, m6: null },
];

const getColor = (value: number | null) => {
  if (value === null) return 'bg-brand-base';
  if (value >= 90) return 'bg-brand-xai text-brand-dark font-semibold';
  if (value >= 75) return 'bg-brand-accent/80 text-white';
  if (value >= 60) return 'bg-brand-accent/50 text-gray-200';
  return 'bg-brand-accent/30 text-gray-400';
};

export const CohortRetentionMatrix: React.FC = () => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-brand-dark p-6 rounded-2xl border border-brand-accent/30 w-full shadow-xl"
    >
      <h3 className="text-white font-medium mb-6">Cohort Retention Matrix</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-xs uppercase text-brand-accent border-b border-brand-accent/20">
            <tr>
              <th className="px-4 py-3">Cohort</th>
              <th className="px-4 py-3">Size</th>
              {[1,2,3,4,5,6].map(m => (
                <th key={m} className="px-4 py-3 text-center">Month {m}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {cohortData.map((row, idx) => (
              <motion.tr 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                key={row.month} 
                className="border-b border-brand-accent/10"
              >
                <td className="px-4 py-3 font-medium text-white">{row.month}</td>
                <td className="px-4 py-3 text-gray-400">{row.size}</td>
                {['m1', 'm2', 'm3', 'm4', 'm5', 'm6'].map(m => {
                  const val = row[m as keyof typeof row] as number | null;
                  return (
                    <td key={m} className="p-1">
                      <div className={`w-full h-full py-2 flex items-center justify-center rounded-md ${getColor(val)} transition-colors`}>
                        {val !== null ? `${val}%` : '-'}
                      </div>
                    </td>
                  );
                })}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};
