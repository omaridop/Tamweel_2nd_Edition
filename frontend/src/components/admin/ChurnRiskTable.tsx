import React from 'react';
import { motion } from 'framer-motion';

const churnData = [
  { id: 'USR-892', name: 'Ahmad Khalil', risk: 'High', lastActive: '45 days', score: 620 },
  { id: 'USR-441', name: 'Sara Othman', risk: 'Medium', lastActive: '21 days', score: 710 },
  { id: 'USR-102', name: 'Zaid Naser', risk: 'Low', lastActive: '2 days', score: 850 },
  { id: 'USR-773', name: 'Rana Yaseen', risk: 'High', lastActive: '60 days', score: 580 },
  { id: 'USR-299', name: 'Omar Ali', risk: 'Medium', lastActive: '18 days', score: 730 },
];

const getBadge = (risk: string) => {
  switch (risk) {
    case 'High': return 'bg-red-500/20 text-red-400 border border-red-500/30';
    case 'Medium': return 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
    case 'Low': return 'bg-brand-xai/20 text-brand-xai border border-brand-xai/30';
    default: return 'bg-gray-500/20 text-gray-400';
  }
};

export const ChurnRiskTable: React.FC = () => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-brand-dark p-6 rounded-2xl border border-brand-accent/30 w-full shadow-xl"
    >
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-white font-medium">Churn Risk Directory</h3>
        <button className="text-xs bg-brand-base border border-brand-accent/40 text-brand-accent px-3 py-1.5 rounded-lg hover:bg-brand-accent hover:text-white transition-colors">
          Export CSV
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-xs uppercase text-brand-accent border-b border-brand-accent/20">
            <tr>
              <th className="px-4 py-3">User ID</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Alt Score</th>
              <th className="px-4 py-3">Last Active</th>
              <th className="px-4 py-3">Risk Level</th>
              <th className="px-4 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {churnData.map((user, idx) => (
              <motion.tr 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                key={user.id} 
                className="border-b border-brand-accent/10 hover:bg-brand-base/50 transition-colors"
              >
                <td className="px-4 py-4 text-gray-300 font-mono text-xs">{user.id}</td>
                <td className="px-4 py-4 text-white font-medium">{user.name}</td>
                <td className="px-4 py-4 text-gray-400">{user.score}</td>
                <td className="px-4 py-4 text-gray-400">{user.lastActive}</td>
                <td className="px-4 py-4">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getBadge(user.risk)}`}>
                    {user.risk}
                  </span>
                </td>
                <td className="px-4 py-4 text-right">
                  <button className="text-brand-accent hover:text-brand-xai transition-colors font-medium text-xs">
                    View Profile
                  </button>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};
