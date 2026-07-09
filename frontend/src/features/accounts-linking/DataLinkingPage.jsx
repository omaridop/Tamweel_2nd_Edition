import { useState, useEffect } from 'react';
import MainLayout from '../../layouts/MainLayout';
import Button from '../../components/ui/Button';
import { ShieldCheck, RefreshCw, Link as LinkIcon, CheckCircle2, AlertCircle, Loader2, X } from 'lucide-react';
import { twMerge } from 'tailwind-merge';
import useConnectionsStore from '../../store/useConnectionsStore';

const ConnectionCard = ({ conn, onRevoke }) => {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-soft hover:border-accent/30 transition-all group">
      <div className="flex justify-between items-start mb-6">
        <div className="w-14 h-14 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center overflow-hidden text-2xl">
          {conn.logo}
        </div>
        <div className={twMerge(
          "px-2.5 py-1 rounded-full text-[10px] font-bold flex items-center",
          conn.status === 'Active' ? "bg-emerald-50 text-emerald-600" :
          conn.status === 'Syncing' ? "bg-blue-50 text-blue-600" : "bg-amber-50 text-amber-600"
        )}>
          {conn.status === 'Syncing' && <RefreshCw className="w-3 h-3 mr-1 animate-spin" />}
          {conn.status === 'Active' && <CheckCircle2 className="w-3 h-3 mr-1" />}
          {conn.status}
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-bold text-primary">{conn.provider}</h3>
        <p className="text-sm text-slate-500">{conn.type}</p>
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-slate-50">
        <span className="text-xs text-slate-400">Last sync: {conn.lastSynced}</span>
        <Button 
          variant="outline" 
          className="h-9 text-xs text-red-500 border-red-200 hover:bg-red-50"
          onClick={() => onRevoke(conn.id)}
        >
          Revoke Access
        </Button>
      </div>
    </div>
  );
};

const AddConnectionModal = ({ isOpen, onClose, availableProviders, onAdd, isAdding }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-primary/40 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl w-full max-w-md overflow-hidden shadow-2xl animate-in zoom-in-95">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
          <h3 className="font-bold text-primary">Connect New Data Source</h3>
          <button onClick={onClose} disabled={isAdding} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6">
          <p className="text-sm text-slate-500 mb-4">Select a provider to securely link to your Tamweel account. Your data is encrypted end-to-end.</p>
          
          <div className="space-y-3">
            {availableProviders.map(provider => (
              <button 
                key={provider.id}
                onClick={() => onAdd(provider.id)}
                disabled={isAdding}
                className="w-full text-left flex items-center p-4 rounded-xl border border-slate-200 hover:border-accent/50 hover:bg-accent/5 transition-all group disabled:opacity-50"
              >
                <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center mr-4 text-xl">
                  {provider.type === 'E-Wallet' ? '📱' : '💳'}
                </div>
                <div>
                  <p className="font-bold text-primary group-hover:text-accent">{provider.name}</p>
                  <p className="text-xs text-slate-500">{provider.type}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const DataLinkingPage = () => {
  const { connections, availableProviders, isLoading, error, fetchConnections, addConnection, revokeConnection } = useConnectionsStore();
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchConnections();
  }, [fetchConnections]);

  const handleAddConnection = async (providerId) => {
    await addConnection(providerId);
    setIsModalOpen(false);
  };

  return (
    <MainLayout>
      {isLoading && !isModalOpen && (
        <div className="fixed inset-0 bg-primary/20 backdrop-blur-sm z-[100] flex items-center justify-center p-6">
           <div className="bg-white p-10 rounded-3xl shadow-2xl flex flex-col items-center max-w-sm w-full animate-in zoom-in-95">
              <div className="relative mb-6">
                <Loader2 className="w-16 h-16 text-accent animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <ShieldCheck className="w-6 h-6 text-accent" />
                </div>
              </div>
              <h3 className="text-xl font-black text-primary text-center">Syncing Connections</h3>
              <p className="text-slate-500 text-center mt-2 font-medium">Please wait while we securely process this request...</p>
           </div>
        </div>
      )}

      <AddConnectionModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        availableProviders={availableProviders}
        onAdd={handleAddConnection}
        isAdding={isLoading}
      />

      <div className="max-w-5xl mx-auto space-y-10 animate-in fade-in duration-500">
        {/* Header with Consent Notice */}
        <div className="bg-primary text-white p-8 rounded-2xl shadow-xl relative overflow-hidden">
          <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div className="max-w-xl">
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-accent/20 text-accent text-xs font-bold mb-4">
                <ShieldCheck className="w-4 h-4 mr-2" />
                Consent Management Center
              </div>
              <h1 className="text-3xl font-bold mb-2">Connected Providers</h1>
              <p className="text-slate-300">
                Manage your open banking and wallet integrations. Connect sources to improve your AI credit score and see all your finances in one place.
              </p>
            </div>
          </div>
          {/* Decorative Background */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-accent opacity-5 blur-3xl -mr-20 -mt-20"></div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-xl shadow-sm animate-in fade-in slide-in-from-top-2">
            <div className="flex">
              <div className="flex-shrink-0">
                <AlertCircle className="h-5 w-5 text-red-500" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700 font-medium">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Connections Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {connections.map((conn) => (
            <ConnectionCard key={conn.id} conn={conn} onRevoke={revokeConnection} />
          ))}

          {/* Add New Source Card */}
          <div 
            onClick={() => setIsModalOpen(true)}
            className="border-2 border-dashed border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center hover:bg-slate-50 hover:border-accent/50 transition-all cursor-pointer group"
          >
             <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mb-4 group-hover:bg-accent group-hover:text-white transition-all text-slate-400">
                <LinkIcon className="w-6 h-6" />
             </div>
             <p className="font-bold text-slate-500 group-hover:text-primary">Add New Connection</p>
             <p className="text-xs text-slate-400 mt-1">E-Wallets, Cards, or Bank</p>
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
                You can revoke access to any connected account at any time, instantly severing the connection.
              </p>
           </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default DataLinkingPage;
