import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/useAuthStore';
import Button from '../components/ui/Button';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

const NotFoundPage = () => {
  const navigate = useNavigate();
  const { token } = useAuthStore();
  const isAuthenticated = !!token;

  const handleReturn = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-bg-subtle flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Decorative Background */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-blob"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10 glass max-w-md w-full p-8 rounded-3xl border border-slate-200 shadow-xl flex flex-col items-center text-center animate-in fade-in zoom-in duration-500">
        <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-6 shadow-inner">
          <ShieldAlert className="w-10 h-10 text-slate-400" />
        </div>
        
        <h1 className="text-6xl font-black text-primary tracking-tight mb-4">404</h1>
        <h2 className="text-xl font-bold text-slate-800 mb-2">Page Not Found</h2>
        <p className="text-slate-500 text-sm mb-8 leading-relaxed">
          The page you are looking for doesn't exist or has been moved. 
          Please double-check the URL or return to safety.
        </p>

        <Button 
          variant="primary" 
          className="w-full flex items-center justify-center gap-2 py-3"
          onClick={handleReturn}
        >
          <ArrowLeft className="w-4 h-4" />
          {isAuthenticated ? 'Return to Dashboard' : 'Go to Login'}
        </Button>
      </div>
    </div>
  );
};

export default NotFoundPage;
