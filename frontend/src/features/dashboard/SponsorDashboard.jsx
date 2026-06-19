import React, { useEffect, useState } from 'react';
import MainLayout from '../../layouts/MainLayout';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { Users as UsersIcon, TrendingUp as TrendIcon, AlertTriangle as AlertIcon, ShieldCheck as ShieldIcon, Search as SearchIcon, Filter as FilterIcon, Loader2 as LoaderIcon } from 'lucide-react';
import Button from '../../components/ui/Button';
import { twMerge } from 'tailwind-merge';
import useAuthStore from '../../store/useAuthStore';
import { useNavigate } from 'react-router-dom';
import { scoringService } from '../../services/api';

const portfolioDistDataTemplate = [
  { name: 'Excellent (80+)', min: 80, max: 100, value: 0, color: '#10B981' },
  { name: 'Good (60-79)', min: 60, max: 79, value: 0, color: '#34D399' },
  { name: 'Fair (40-59)', min: 40, max: 59, value: 0, color: '#FBBF24' },
  { name: 'Poor (20-39)', min: 20, max: 39, value: 0, color: '#F87171' },
  { name: 'Very Poor (<20)', min: 0, max: 19, value: 0, color: '#EF4444' },
];

const SponsorDashboard = () => {
  const { user, role } = useAuthStore();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (role !== 'sponsor') {
       navigate('/user/dashboard');
    }
  }, [role, navigate]);
  const [data, setData] = useState([]);
  const [stats, setStats] = useState([]);
  const [distData, setDistData] = useState(portfolioDistDataTemplate);

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const responseData = await scoringService.getAllResults();
        setData(responseData);
        calculateStats(responseData);
      } catch (error) {
        console.error("Sponsor Portfolio Error:", error);
      } finally {
        setLoading(false);
      }
    };

    const calculateStats = (records) => {
        const avgScore = records.reduce((acc, curr) => acc + curr.credit_score, 0) / records.length;
        const totalBorrowers = records.length;
        const defaultRisk = (records.filter(r => r.credit_score < 30).length / records.length) * 100;
        
        setStats([
            { label: 'Total Borrowers', value: totalBorrowers.toString(), change: '+4', icon: UsersIcon, color: 'text-blue-500' },
            { label: 'Avg. Credit Score', value: avgScore.toFixed(0), change: '+2 pts', icon: TrendIcon, color: 'text-accent' },
            { label: 'Default Risk', value: defaultRisk.toFixed(1) + '%', change: '-0.5%', icon: AlertIcon, color: 'text-red-500' },
            { label: 'Portfolio Health', value: 'Healthy', change: 'Stable', icon: ShieldIcon, color: 'text-emerald-500' },
        ]);

        const newDist = portfolioDistDataTemplate.map(tier => ({
            ...tier,
            value: records.filter(r => r.credit_score >= tier.min && r.credit_score <= tier.max).length
        }));
        setDistData(newDist);
    }

    fetchPortfolio();
  }, []);

  if (loading) {
    return (
      <MainLayout>
        <div className="h-[60vh] flex flex-col items-center justify-center text-slate-400">
           <LoaderIcon className="w-10 h-10 animate-spin mb-4 text-accent" />
           <p className="font-bold">Loading Institutional Portfolio...</p>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-primary">Lender Portfolio Overview</h1>
            <p className="text-slate-500 font-medium">Real-time risk metrics and borrower distribution.</p>
          </div>
          <div className="flex gap-3">
             <div className="relative">
                <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input className="pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-accent" placeholder="Search Portfolio..." />
             </div>
             <Button variant="outline" className="h-10">
                <FilterIcon className="w-4 h-4 mr-2" />
                Filter
             </Button>
          </div>
        </div>

        {/* High Level Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
           {stats.map((stat) => (
             <div key={stat.label} className="bg-white p-6 rounded-2xl shadow-soft border border-slate-100">
                <div className="flex justify-between items-start">
                   <div className={`p-2 rounded-lg bg-slate-50 ${stat.color}`}>
                      <stat.icon className="w-5 h-5" />
                   </div>
                   <span className="text-xs font-bold text-emerald-500">{stat.change}</span>
                </div>
                <div className="mt-4">
                   <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">{stat.label}</p>
                   <p className="text-2xl font-black text-primary mt-1">{stat.value}</p>
                </div>
             </div>
           ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
           {/* Score Distribution */}
           <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100">
              <h3 className="font-bold text-primary mb-8">Score Distribution Tier</h3>
              <div className="h-72 w-full">
                 <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={distData} layout="vertical">
                       <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#F1F5F9" />
                       <XAxis type="number" hide />
                       <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} width={150} tick={{fill: '#64748B', fontSize: 11, fontWeight: 'bold'}} />
                       <Tooltip cursor={{fill: 'transparent'}} contentStyle={{ borderRadius: '12px', border: 'none' }} />
                       <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={30}>
                          {distData.map((entry, index) => (
                             <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                       </Bar>
                    </BarChart>
                 </ResponsiveContainer>
              </div>
           </div>

           {/* Risk Trends */}
           <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100">
              <h3 className="font-bold text-primary mb-8">Portfolio Risk Distribution (%)</h3>
              <div className="h-72 w-full">
                 <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                       <Pie
                          data={distData}
                          innerRadius={80}
                          outerRadius={110}
                          paddingAngle={5}
                          dataKey="value"
                       >
                          {distData.map((entry, index) => (
                             <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                       </Pie>
                       <Tooltip />
                    </PieChart>
                 </ResponsiveContainer>
              </div>
           </div>
        </div>

        {/* Recent Applications Table */}
        <div className="bg-white rounded-3xl shadow-soft border border-slate-100 overflow-hidden">
           <div className="p-8 border-b border-slate-50 flex justify-between items-center">
              <h3 className="font-bold text-primary">Live Credit Assessments</h3>
              <Button variant="ghost" className="text-xs font-bold text-accent">Export Report</Button>
           </div>
           <div className="overflow-x-auto">
              <table className="w-full text-left">
                 <thead className="bg-slate-50 text-slate-400 text-[10px] font-bold uppercase tracking-widest">
                    <tr>
                       <th className="px-8 py-4">Applicant</th>
                       <th className="px-8 py-4">AI Score</th>
                       <th className="px-8 py-4">Amount (JOD)</th>
                       <th className="px-8 py-4">Risk Level</th>
                       <th className="px-8 py-4">Date</th>
                    </tr>
                 </thead>
                 <tbody className="divide-y divide-slate-50 text-sm">
                    {data.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50 transition-all">
                         <td className="px-8 py-4 font-bold text-primary">{row.name}</td>
                         <td className="px-8 py-4">
                            <span className={twMerge(
                               "px-2 py-1 rounded-lg text-xs font-bold",
                               row.credit_score > 60 ? "bg-emerald-50 text-emerald-600" : 
                               row.credit_score > 30 ? "bg-amber-50 text-amber-600" : "bg-red-50 text-red-600"
                            )}>{row.credit_score}</span>
                         </td>
                         <td className="px-8 py-4 font-medium text-slate-600">{row.approved_amount_jod}</td>
                         <td className="px-8 py-4 text-slate-400">{row.risk_level}</td>
                         <td className="px-8 py-4 text-slate-400">{new Date(row.generated_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                 </tbody>
              </table>
           </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default SponsorDashboard;
