import { useEffect, useState, useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { TrendingUp, AlertCircle } from 'lucide-react';

const COLORS = ['#10B981', '#F87171', '#3B82F6', '#F59E0B', '#8B5CF6', '#EC4899', '#64748B'];

import { fetchWithAuth } from '../../services/api';

const SpendingAnalytics = ({ userEmail }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (!userEmail) {
        setLoading(false);
        return;
      }
      try {
        const result = await fetchWithAuth(`/analytics/spending-patterns/${userEmail}`);
        setData(result);
      } catch {
        // Do nothing on error
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [userEmail]);

  // Process data for Donut Chart (Expenses by Category)
  const donutData = useMemo(() => {
    if (!data || !data.transactions) return [];
    const expenses = data.transactions.filter(t => t.type === 'expense');
    const categoryMap = expenses.reduce((acc, curr) => {
      acc[curr.category] = (acc[curr.category] || 0) + Number(curr.amount);
      return acc;
    }, {});
    
    return Object.keys(categoryMap).map(key => ({
      name: key.replace('_', ' ').toUpperCase(),
      value: categoryMap[key]
    })).sort((a, b) => b.value - a.value);
  }, [data]);

  // Process data for Trend Line (Income vs Expense over time)
  // Group by Month
  const trendData = useMemo(() => {
    if (!data || !data.transactions) return [];
    const monthlyMap = data.transactions.reduce((acc, curr) => {
      const date = new Date(curr.created_at);
      const month = date.toLocaleString('default', { month: 'short' });
      if (!acc[month]) acc[month] = { month, income: 0, expense: 0 };
      acc[month][curr.type] += Number(curr.amount);
      return acc;
    }, {});

    return Object.values(monthlyMap);
  }, [data]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full mt-8">
        <div className="bg-slate-100 animate-pulse h-80 rounded-3xl w-full"></div>
        <div className="bg-slate-100 animate-pulse h-80 rounded-3xl w-full"></div>
      </div>
    );
  }

  if (!data || !data.transactions || data.transactions.length === 0) {
    return (
      <div className="h-64 flex flex-col items-center justify-center text-slate-400 bg-white rounded-3xl border border-slate-100 shadow-sm p-6 text-center mt-8">
        <AlertCircle className="w-8 h-8 mb-4 text-slate-300" />
        <p className="font-bold text-sm text-slate-500">No transaction data available.</p>
        <p className="text-xs mt-1 text-slate-400">Connect your bank account to unlock spending analytics.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Category Donut Chart */}
      <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100">
        <div className="flex justify-between items-center mb-8">
          <h3 className="font-bold text-slate-900">Expense Distribution</h3>
          <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-lg text-[10px] font-bold uppercase tracking-wider">Top: {donutData[0]?.name || 'N/A'}</span>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={donutData}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={85}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {donutData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value) => [`${value.toFixed(2)} JOD`, 'Amount']}
                contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                itemStyle={{ color: '#1E293B', fontWeight: 600 }}
              />
              <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#64748B' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Income vs Expenses Trend Line */}
      <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100">
        <div className="flex justify-between items-center mb-8">
          <h3 className="font-bold text-slate-900">Cash Flow Trend</h3>
          <div className="flex items-center text-emerald-600 font-bold bg-emerald-50 px-3 py-1 rounded-lg text-[10px] uppercase tracking-wider">
            <TrendingUp className="w-3.5 h-3.5 mr-1.5" />
            Savings Rate: {(data.metrics.savings_rate * 100).toFixed(1)}%
          </div>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
              <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#94A3B8', fontSize: 12, fontWeight: 500}} dy={10} />
              <YAxis hide />
              <Tooltip 
                contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                formatter={(value) => [`${value.toFixed(2)} JOD`]}
                itemStyle={{ fontWeight: 600 }}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#64748B' }} />
              <Line type="monotone" dataKey="income" name="Income" stroke="#10B981" strokeWidth={3} dot={{ r: 4, strokeWidth: 2, fill: '#fff' }} activeDot={{ r: 6, fill: '#10B981', strokeWidth: 0 }} />
              <Line type="monotone" dataKey="expense" name="Expenses" stroke="#F87171" strokeWidth={3} dot={{ r: 4, strokeWidth: 2, fill: '#fff' }} activeDot={{ r: 6, fill: '#F87171', strokeWidth: 0 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default SpendingAnalytics;
