import { useEffect, useState, useRef } from 'react';
import MainLayout from '../../layouts/MainLayout';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { Users as UsersIcon, TrendingUp as TrendIcon, AlertTriangle as AlertIcon, ShieldCheck as ShieldIcon, Search as SearchIcon, Filter as FilterIcon, Loader2 as LoaderIcon, FileText, CheckCircle2, XCircle, Upload as UploadIcon } from 'lucide-react';
import Button from '../../components/ui/Button';
import { twMerge } from 'tailwind-merge';
import useAuthStore from '../../store/useAuthStore';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { scoringService } from '../../services/api';

const portfolioDistDataTemplate = [
  { name: 'Excellent (80+)', min: 80, max: 100, value: 0, color: '#10B981' },
  { name: 'Good (60-79)', min: 60, max: 79, value: 0, color: '#34D399' },
  { name: 'Fair (40-59)', min: 40, max: 59, value: 0, color: '#FBBF24' },
  { name: 'Poor (20-39)', min: 20, max: 39, value: 0, color: '#F87171' },
  { name: 'Very Poor (<20)', min: 0, max: 19, value: 0, color: '#EF4444' },
];

const MOCK_KYC_QUEUE = [
  { id: '1', name: 'Rami N.', docType: 'National ID', submitted: '10 mins ago', riskScore: 'Low', status: 'Pending Review' },
  { id: '2', name: 'Laila H.', docType: 'Passport', submitted: '1 hour ago', riskScore: 'High', status: 'Flagged (Mismatch)' },
  { id: '3', name: 'Khaled J.', docType: 'National ID', submitted: '2 hours ago', riskScore: 'Medium', status: 'Pending Review' },
];

const SponsorDashboard = () => {
  const { role } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    if (file.type !== "application/pdf") {
      alert("Please upload a PDF file.");
      return;
    }

    setIsUploading(true);
    try {
      await scoringService.uploadPolicy(file);
      alert("File uploaded and processed successfully.");
    } catch (err) {
      alert("Error uploading file: " + err.message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // Derive active tab from URL path
  const activeTab = location.pathname.includes('kyc') ? 'kyc' : 
                    location.pathname.includes('risk') ? 'risk' : 'overview';

  useEffect(() => {
    if (role !== 'sponsor' && role !== 'admin') {
       navigate('/dashboard');
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
      } catch {
        // Do nothing on error
      } finally {
        setLoading(false);
      }
    };

    const calculateStats = (records) => {
        const avgScore = records.reduce((acc, curr) => acc + curr.credit_score, 0) / records.length || 0;
        const totalBorrowers = records.length;
        
        
        setStats([
            { label: 'Active Users', value: totalBorrowers.toString(), change: '+12', icon: UsersIcon, color: 'text-blue-500' },
            { label: 'Avg. AI Score', value: avgScore.toFixed(0), change: '+5 pts', icon: TrendIcon, color: 'text-accent' },
            { label: 'High Risk Alerts', value: records.filter(r => r.credit_score < 30).length.toString(), change: '+1', icon: AlertIcon, color: 'text-red-500' },
            { label: 'KYC Backlog', value: '3', change: 'Needs Action', icon: ShieldIcon, color: 'text-amber-500' },
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
           <p className="font-bold">Loading Command Center...</p>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
        
        {/* Header & Internal Nav */}
        <div className="flex flex-col space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-primary">Admin Command Center</h1>
              <p className="text-slate-500 font-medium mt-1">Real-time system health, compliance, and risk metrics.</p>
            </div>
            <div className="flex gap-3">
               <input 
                 type="file" 
                 accept=".pdf" 
                 ref={fileInputRef} 
                 onChange={handleFileUpload} 
                 className="hidden" 
               />
               <Button variant="primary" className="h-10 bg-accent text-white" onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
                  {isUploading ? <LoaderIcon className="w-4 h-4 mr-2 animate-spin inline" /> : <UploadIcon className="w-4 h-4 mr-2 inline" />}
                  {isUploading ? "Uploading..." : "Upload a file"}
               </Button>
               <div className="relative hidden sm:block">
                  <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input className="pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-accent" placeholder="Search Users ID..." />
               </div>
               <Button variant="outline" className="h-10">
                  <FilterIcon className="w-4 h-4 mr-2" />
                  Filter
               </Button>
            </div>
          </div>

          {/* Sub Navigation */}
          <div className="flex gap-2 border-b border-slate-200 pb-px">
            <Link to="/admin" className={twMerge("px-4 py-2 border-b-2 font-bold transition-all text-sm", activeTab === 'overview' ? "border-accent text-accent" : "border-transparent text-slate-400 hover:text-slate-600")}>
              System Overview
            </Link>
            <Link to="/admin/kyc" className={twMerge("px-4 py-2 border-b-2 font-bold transition-all text-sm flex items-center", activeTab === 'kyc' ? "border-accent text-accent" : "border-transparent text-slate-400 hover:text-slate-600")}>
              KYC Queue
              <span className="ml-2 bg-red-100 text-red-600 px-1.5 py-0.5 rounded-full text-[10px]">3</span>
            </Link>
            <Link to="/admin/risk" className={twMerge("px-4 py-2 border-b-2 font-bold transition-all text-sm", activeTab === 'risk' ? "border-accent text-accent" : "border-transparent text-slate-400 hover:text-slate-600")}>
              Risk Management
            </Link>
          </div>
        </div>

        {/* --- SYSTEM OVERVIEW TAB --- */}
        {activeTab === 'overview' && (
          <div className="space-y-8 animate-in slide-in-from-right-4 duration-300">
            {/* High Level Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
               {stats.map((stat) => (
                 <div key={stat.label} className="bg-white p-6 rounded-2xl shadow-soft border border-slate-100">
                    <div className="flex justify-between items-start">
                       <div className={`p-2 rounded-lg bg-slate-50 ${stat.color}`}>
                          <stat.icon className="w-5 h-5" />
                       </div>
                       <span className={twMerge("text-xs font-bold", stat.change.includes('-') || stat.change.includes('Action') ? "text-red-500" : "text-emerald-500")}>
                         {stat.change}
                       </span>
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
               <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100">
                  <h3 className="font-bold text-primary mb-8">Platform Health Distribution</h3>
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

               <div className="bg-white p-8 rounded-3xl shadow-soft border border-slate-100">
                  <h3 className="font-bold text-primary mb-8">Risk Segments (%)</h3>
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
          </div>
        )}

        {/* --- KYC QUEUE TAB --- */}
        {activeTab === 'kyc' && (
          <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
             <div className="bg-white rounded-3xl shadow-soft border border-slate-100 overflow-hidden">
                <div className="p-8 border-b border-slate-50 flex justify-between items-center">
                   <div>
                     <h3 className="font-bold text-primary text-lg">Identity Verification Queue</h3>
                     <p className="text-sm text-slate-500">Requires manual human review for edge cases or flagged ML OCR results.</p>
                   </div>
                </div>
                <div className="divide-y divide-slate-50">
                  {MOCK_KYC_QUEUE.map(item => (
                    <div key={item.id} className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50 transition-colors">
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center text-slate-400">
                          <FileText className="w-6 h-6" />
                        </div>
                        <div>
                          <h4 className="font-bold text-primary">{item.name}</h4>
                          <p className="text-xs text-slate-500 mt-1">Submitted {item.submitted} • {item.docType}</p>
                          <span className={twMerge("inline-block mt-2 px-2 py-0.5 rounded text-[10px] font-bold", item.riskScore === 'High' ? "bg-red-100 text-red-600" : "bg-blue-100 text-blue-600")}>
                             {item.status}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" className="h-9 text-xs">View Docs</Button>
                        <Button variant="primary" className="h-9 bg-emerald-500 hover:bg-emerald-600 text-white text-xs border-emerald-500 px-3">
                           <CheckCircle2 className="w-4 h-4 mr-1" /> Approve
                        </Button>
                        <Button variant="outline" className="h-9 text-red-500 border-red-200 hover:bg-red-50 text-xs px-3">
                           <XCircle className="w-4 h-4 mr-1" /> Reject
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
             </div>
          </div>
        )}

        {/* --- RISK MANAGEMENT TAB --- */}
        {activeTab === 'risk' && (
          <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
             <div className="bg-white rounded-3xl shadow-soft border border-slate-100 overflow-hidden">
                <div className="p-8 border-b border-slate-50 flex justify-between items-center">
                   <div>
                     <h3 className="font-bold text-primary text-lg">Live User Risk Monitoring</h3>
                     <p className="text-sm text-slate-500">Track and freeze anomalous behavior and score drops across the user base.</p>
                   </div>
                   <Button variant="ghost" className="text-xs font-bold text-accent">Export Report</Button>
                </div>
                <div className="overflow-x-auto">
                   <table className="w-full text-left">
                      <thead className="bg-slate-50 text-slate-400 text-[10px] font-bold uppercase tracking-widest">
                         <tr>
                            <th className="px-8 py-4">User</th>
                            <th className="px-8 py-4">Current Score</th>
                            <th className="px-8 py-4">Risk Level</th>
                            <th className="px-8 py-4">Last Monitored</th>
                            <th className="px-8 py-4 text-right">Actions</th>
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
                              <td className="px-8 py-4 text-slate-400 font-medium">
                                {row.credit_score > 60 ? 'Low' : row.credit_score > 30 ? 'Medium' : 'High'}
                              </td>
                              <td className="px-8 py-4 text-slate-400">{new Date(row.generated_at).toLocaleDateString()}</td>
                              <td className="px-8 py-4 text-right">
                                <Button variant="outline" className="h-8 text-[10px] px-3 border-slate-200">Investigate</Button>
                              </td>
                           </tr>
                         ))}
                      </tbody>
                   </table>
                </div>
             </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default SponsorDashboard;
