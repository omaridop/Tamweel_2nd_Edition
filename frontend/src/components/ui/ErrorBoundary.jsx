import { Component } from 'react';
import { AlertTriangle } from 'lucide-react';
import Button from './Button';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-bg-subtle flex flex-col items-center justify-center p-4">
          <div className="glass max-w-md w-full p-8 rounded-3xl border border-slate-200 shadow-xl flex flex-col items-center text-center animate-in fade-in zoom-in duration-500">
            <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-6">
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
            
            <h2 className="text-xl font-bold text-slate-800 mb-2">Something went wrong</h2>
            <p className="text-slate-500 text-sm mb-4 leading-relaxed">
              We encountered an unexpected error. Our team has been notified.
            </p>

            <div className="bg-red-50/50 border border-red-100 rounded-lg p-3 w-full mb-6 text-left overflow-hidden">
              <p className="text-xs font-mono text-red-600 mb-1 font-semibold">{this.state.error?.toString()}</p>
              <p className="text-[10px] font-mono text-red-400 break-words">{this.state.error?.stack?.substring(0, 200)}</p>
            </div>
            
            <Button 
              variant="primary" 
              className="w-full"
              onClick={() => window.location.href = '/dashboard'}
            >
              Reload Application
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
