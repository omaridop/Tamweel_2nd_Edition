import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const data = [
  { name: 'Wallet Velocity', weight: 45 },
  { name: 'Utility Consistency', weight: 30 },
  { name: 'Network Metadata', weight: 15 },
  { name: 'Geolocation', weight: 10 },
];

export const XAIChart: React.FC = () => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-brand-dark p-6 rounded-2xl border border-brand-accent/30 w-full h-80 shadow-xl"
    >
      <h3 className="text-brand-xai font-medium mb-6 flex items-center gap-3">
        <span className="w-2.5 h-2.5 rounded-full bg-brand-xai animate-pulse shadow-[0_0_8px_#10B981]" />
        Explainable AI Factors
      </h3>
      <div className="h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 30, right: 20 }}>
            <XAxis type="number" hide />
            <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#94A3B8', fontSize: 13 }} width={120} />
            <Tooltip 
              cursor={{ fill: 'rgba(13, 148, 136, 0.1)' }}
              contentStyle={{ backgroundColor: '#020617', border: '1px solid #0D9488', borderRadius: '8px', color: '#fff' }}
              itemStyle={{ color: '#10B981' }}
            />
            <Bar dataKey="weight" radius={[0, 6, 6, 0]} barSize={24}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={index === 0 ? '#10B981' : '#0D9488'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
};
