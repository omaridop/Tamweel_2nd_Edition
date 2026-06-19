import React from 'react';
import MainLayout from '../../layouts/MainLayout';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import { ShieldAlert, Send, FileText, CheckCircle } from 'lucide-react';

const DisputeResolutionPage = () => {
  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto space-y-10 animate-in fade-in duration-500">
        <div className="text-center space-y-3">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-red-50 text-red-500 mb-2">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-bold text-primary">Consumer Rights & Disputes</h1>
          <p className="text-slate-500 max-w-xl mx-auto">
            Report inaccurate data or appeal a credit decision. We follow World Bank guidelines 
            to ensure fair and transparent data processing.
          </p>
        </div>

        <div className="bg-white rounded-3xl shadow-soft border border-slate-100 overflow-hidden">
          <div className="p-8 border-b border-slate-50 bg-slate-50/50">
             <h3 className="font-bold text-primary">Submit a Formal Dispute</h3>
             <p className="text-xs text-slate-400 mt-1">Typical resolution time: 5-7 business days.</p>
          </div>
          
          <form className="p-8 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <Input label="Dispute Type" placeholder="e.g., Inaccurate Payment History" />
               <Input label="Related Account" placeholder="e.g., ZainCash Wallet" />
            </div>

            <div className="space-y-1.5">
               <label className="text-sm font-semibold text-slate-700 ml-1">Detailed Description</label>
               <textarea 
                 className="w-full min-h-[150px] rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 transition-all"
                 placeholder="Please explain the discrepancy in detail..."
               ></textarea>
            </div>

            <div className="p-4 border-2 border-dashed border-slate-100 rounded-2xl flex flex-col items-center justify-center py-10 bg-slate-50/30">
               <FileText className="w-8 h-8 text-slate-300 mb-2" />
               <p className="text-sm font-bold text-slate-500">Upload Supporting Evidence</p>
               <p className="text-xs text-slate-400">PDF, JPG or PNG (Max 5MB)</p>
               <Button variant="outline" className="mt-4 h-8 text-xs">Browse Files</Button>
            </div>

            <div className="flex items-center gap-3 pt-4 border-t border-slate-50">
               <Button type="submit" variant="primary" className="flex-1 h-12">
                  <Send className="w-4 h-4 mr-2" />
                  Submit Dispute
               </Button>
               <Button variant="outline" className="h-12 px-8">Cancel</Button>
            </div>
          </form>
        </div>

        {/* Regulatory Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
           <div className="p-6 bg-white rounded-2xl border border-slate-100 shadow-sm flex gap-4">
              <CheckCircle className="text-emerald-500 w-5 h-5 shrink-0" />
              <div>
                 <h4 className="text-sm font-bold text-primary">Fair Credit Reporting</h4>
                 <p className="text-xs text-slate-500 mt-1">Your score will be marked "Under Dispute" while we investigate.</p>
              </div>
           </div>
           <div className="p-6 bg-white rounded-2xl border border-slate-100 shadow-sm flex gap-4">
              <CheckCircle className="text-emerald-500 w-5 h-5 shrink-0" />
              <div>
                 <h4 className="text-sm font-bold text-primary">Data Protection</h4>
                 <p className="text-xs text-slate-500 mt-1">Dispute data is encrypted and only visible to authorized auditors.</p>
              </div>
           </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default DisputeResolutionPage;
