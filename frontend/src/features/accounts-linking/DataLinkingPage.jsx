import React, { useState } from 'react';
import MainLayout from '../../layouts/MainLayout';
import Button from '../../components/ui/Button';
import { ShieldCheck, RefreshCw, Link as LinkIcon, CheckCircle2, AlertCircle, Wallet, Loader2 } from 'lucide-react';
import { twMerge } from 'tailwind-merge';
import { useNavigate } from 'react-router-dom';
import { scoringService } from '../../services/api';
import useAuthStore from '../../store/useAuthStore';

const ConnectionCard = ({ conn, onConnect }) => {
  const [imgError, setImgError] = useState(false);

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-soft hover:border-accent/30 transition-all group">
      <div className="flex justify-between items-start mb-6">
        <div className="w-14 h-14 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center overflow-hidden">
          {imgError ? (
            <Wallet className="w-8 h-8 text-slate-300" />
          ) : (
            <img 
              src={conn.icon} 
              alt={conn.name} 
              className="w-10 h-10 object-contain grayscale group-hover:grayscale-0 transition-all"
              onError={() => setImgError(true)}
            />
          )}
        </div>
        <div className={twMerge(
          "px-2.5 py-1 rounded-full text-[10px] font-bold flex items-center",
          conn.status === 'Connected' ? "bg-emerald-50 text-emerald-600" :
          conn.status === 'Syncing' ? "bg-blue-50 text-blue-600" : "bg-slate-100 text-slate-500"
        )}>
          {conn.status === 'Syncing' && <RefreshCw className="w-3 h-3 mr-1 animate-spin" />}
          {conn.status === 'Connected' && <CheckCircle2 className="w-3 h-3 mr-1" />}
          {conn.status}
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-bold text-primary">{conn.name}</h3>
        <p className="text-sm text-slate-500">{conn.type}</p>
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-slate-50">
        <span className="text-xs text-slate-400">Last sync: {conn.lastSync}</span>
        <Button 
          variant={conn.status === 'Connected' ? "outline" : "primary"} 
          className="h-9 text-xs"
          onClick={() => onConnect(conn)}
        >
          {conn.status === 'Connected' ? 'Manage' : 'Connect'}
        </Button>
      </div>
    </div>
  );
};

const DataLinkingPage = () => {
  const navigate = useNavigate();
  const { user, setDetailedAssessment } = useAuthStore();
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState('');

  const [connections] = useState([
    { id: 'zain', name: 'ZainCash', type: 'Mobile Wallet', status: 'Connected', lastSync: '2 hours ago', icon: '/logos/zaincash.png' },
    { id: 'cliq', name: 'CliQ', type: 'Instant Payment', status: 'Disconnected', lastSync: 'Never', icon: '/logos/cliq.png' },
    { id: 'bank', name: 'Arab Bank', type: 'Credit Card', status: 'Disconnected', lastSync: 'Never', icon: '/logos/arabbank.png' },
  ]);

  const handleConnect = async (conn) => {
    if (conn.status === 'Connected') return;

    setIsSyncing(true);
    setSyncMessage(`Connecting to ${conn.name}...`);

    try {
      // Simulate OAuth/Connection process
      await new Promise(resolve => setTimeout(resolve, 1500));
      setSyncMessage('Extracting 12-month billing history...');
      await new Promise(resolve => setTimeout(resolve, 1500));
      setSyncMessage('Running Tamweel AI Credit Assessment...');

      // Mock User Data for Scoring
      const mockUserData = {
        name: user?.name || "Anas",
        profession: "Software Engineer",
        profession_category: "freelance",
        avg_monthly_income_jod: 850.0,
        income_stability_score: 0.88,
        income_source_count: 2,
        late_bills_count: 1,
        bill_reliability_pct: 92.0,
        total_bills_checked: 24,
        current_balance_jod: 350.0,
        wallet_tx_count: 42,
        wallet_total_volume_jod: 1500.0,
        balance_to_income_ratio: 0.41,
        existing_loans: 0
      };

      const result = await scoringService.getScore(mockUserData);
      setDetailedAssessment(result);
      
      setSyncMessage('Score generated successfully!');
      await new Promise(resolve => setTimeout(resolve, 1000));
      navigate('/user/dashboard');
    } catch (error) {
      console.error("Connection/Scoring Error:", error);
      alert("Failed to connect account. Please try again.");
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <MainLayout>
      {isSyncing && (
        <div className="fixed inset-0 bg-primary/20 backdrop-blur-sm z-[100] flex items-center justify-center p-6">
           <div className="bg-white p-10 rounded-3xl shadow-2xl flex flex-col items-center max-w-sm w-full animate-in zoom-in-95">
              <div className="relative mb-6">
                <Loader2 className="w-16 h-16 text-accent animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <ShieldCheck className="w-6 h-6 text-accent" />
                </div>
              </div>
              <h3 className="text-xl font-black text-primary text-center">AI Data Sync</h3>
              <p className="text-slate-500 text-center mt-2 font-medium">{syncMessage}</p>
           </div>
        </div>
      )}

      <div className="max-w-5xl mx-auto space-y-10 animate-in fade-in duration-500">
        {/* Header with Consent Notice */}
        <div className="bg-primary text-white p-8 rounded-2xl shadow-xl relative overflow-hidden">
          <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div className="max-w-xl">
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-accent/20 text-accent text-xs font-bold mb-4">
                <ShieldCheck className="w-4 h-4 mr-2" />
                World Bank Compliant Consent
              </div>
              <h1 className="text-3xl font-bold mb-2">Connect Financial Sources</h1>
              <p className="text-slate-300">
                To generate your AI credit score, we analyze alternative data patterns. 
                Your data is encrypted and used only for credit assessment.
              </p>
            </div>
            <Button variant="accent" className="h-12 px-8">Read Consent Policy</Button>
          </div>
          {/* Decorative Background */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-accent opacity-5 blur-3xl -mr-20 -mt-20"></div>
        </div>

        {/* Connections Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {connections.map((conn) => (
            <ConnectionCard key={conn.id} conn={conn} onConnect={handleConnect} />
          ))}

          {/* Add New Source Card */}
          <div className="border-2 border-dashed border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center hover:bg-slate-50 transition-all cursor-pointer group">
             <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mb-4 group-hover:bg-accent group-hover:text-white transition-all text-slate-400">
                <LinkIcon className="w-6 h-6" />
             </div>
             <p className="font-bold text-slate-500 group-hover:text-primary">Add New Data Source</p>
             <p className="text-xs text-slate-400 mt-1">Utility, Rent, or Bank</p>
          </div>
        </div>

        {/* Security Info Card */}
        <div className="glass p-6 rounded-2xl flex items-start gap-4 border-emerald-100 shadow-sm">
           <div className="p-3 bg-emerald-50 rounded-xl">
              <AlertCircle className="text-accent w-6 h-6" />
           </div>
           <div>
              <h4 className="font-bold text-primary">Your Data Privacy is Guaranteed</h4>
              <p className="text-sm text-slate-600 mt-1">
                We use 256-bit bank-level encryption. We never sell your personal financial data to third parties. 
                You can revoke access to any connected account at any time.
              </p>
           </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default DataLinkingPage;
