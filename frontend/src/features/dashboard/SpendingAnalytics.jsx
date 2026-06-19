import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { Loader2, TrendingUp, AlertCircle } from 'lucide-react';

const COLORS = ['#10B981', '#F87171', '#3B82F6', '#F59E0B', '#8B5CF6', '#EC4899', '#64748B'];

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
        const response = await fetch(`http://localhost:8000/api/v1/analytics/spending-patterns/${userEmail}`);
        if (response.ok) {
          const result = await response.json();
          setData(result);
        }
      } catch (error) {
        console.error('Failed to fetch analytics', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [userEmail]);

  if (loading) {
    return (
      <div className="h-64 flex flex-col items-center justify-center text-slate-400 bg-white rounded-3xl border border-slate-100 shadow-soft">
        <Loader2 className="w-8 h-8 animate-spin mb-4 text-accent" />
        <p className="font-bold text-sm">Analyzing Spending Patterns...</p>
      </div>
    );
  }

  if (!data || !data.transactions || data.transactions.length === 0) {
    return (
      <div className="h-64 flex flex-col items-center justify-center text-slate-400 bg-white rounded-3xl border border-slate-100 shadow-soft p-6 text-center">
        <AlertCircle className="w-8 h-8 mb-4 text-slate-300" />
        <p className="font-bold text-sm">No transaction data available.</p>
        <p className="text-xs mt-1">Connect your bank account to unlock spending analytics.</p>
      </div>
    );
  }

  // Process data for Donut Chart (Expenses by Category)
  const expenses = data.transactions.filter(t => t.type === 'expense');
  const categoryMap = expenses.reduce((acc, curr) => {
    acc[curr.category] = (acc[curr.category] || 0) + Number(curr.amount);
    return acc;
  }, {});
  
  const donutData = Object.keys(categoryMap).map(key => ({
    name: key.replace('_', ' ').toUpperCase(),
    value: categoryMap[key]
  })).sort((a, b) => b.value - a.value);

  // Process data for Trend Line (Income vs Expense over time)
  // Group by Month
  const monthlyMap = data.transactions.reduce((acc, curr) => {
    const date = new Date(curr.created_at);
    const month = date.toLocaleString('default', { month: 'short' });
    if (!acc[month]) acc[month] = { month, income: 0, expense: 0 };
    acc[month][curr.type] += Number(curr.amount);
    return acc;
  }, {});

  const trendData = Object.values(monthlyMap);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Category Donut Chart */}
      <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100">
        <div className="flex justify-between items-center mb-6">
          <h3 className="font-bold text-primary">Expense Distribution</h3>
          <span className="px-3 py-1 bg-slate-50 text-slate-500 rounded-full text-xs font-bold">Top: {donutData[0]?.name || 'N/A'}</span>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={donutData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {donutData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value) => [`${value.toFixed(2)} JOD`, 'Amount']}
                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
              />
              <Legend verticalAlign="bottom" height={36} iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Income vs Expenses Trend Line */}
      <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100">
        <div className="flex justify-between items-center mb-6">
          <h3 className="font-bold text-primary">Cash Flow Trend</h3>
          <div className="flex items-center text-emerald-500 font-bold bg-emerald-50 px-3 py-1 rounded-full text-xs">
            <TrendingUp className="w-4 h-4 mr-1" />
            Savings Rate: {(data.metrics.savings_rate * 100).toFixed(1)}%
          </div>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
              <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#94A3B8', fontSize: 12}} dy={10} />
              <YAxis hide />
              <Tooltip 
                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                formatter={(value) => [`${value.toFixed(2)} JOD`]}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" />
              <Line type="monotone" dataKey="income" name="Income" stroke="#10B981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              <Line type="monotone" dataKey="expense" name="Expenses" stroke="#F87171" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default SpendingAnalytics;
