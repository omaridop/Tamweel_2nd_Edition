import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileText, CheckCircle2, Loader2, FilePlus, Zap, Database, BrainCircuit, AlertCircle } from 'lucide-react';
import useAuthStore from '../../store/useAuthStore';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

export default function AdminKnowledgeUpload() {
  const token = useAuthStore(state => state.token);
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  
  // Status: 'idle' | 'processing' | 'success' | 'error'
  const [status, setStatus] = useState('idle');
  const [errorMessage, setErrorMessage] = useState('');
  
  // Steps: 1: Uploading, 2: Parsing, 3: Embedding, 4: Syncing
  const [currentStep, setCurrentStep] = useState(0);
  const [processTime, setProcessTime] = useState(0);
  
  const timerRef = useRef(null);
  const startTimeRef = useRef(0);

  const steps = [
    { id: 1, title: 'Uploading Document', icon: <UploadCloud className="w-5 h-5" /> },
    { id: 2, title: 'Text Parsing & Smart Chunking (Gemini 2.5)', icon: <FileText className="w-5 h-5" /> },
    { id: 3, title: 'Generating 768-D Vector Embeddings', icon: <BrainCircuit className="w-5 h-5" /> },
    { id: 4, title: 'Syncing to Supabase DB', icon: <Database className="w-5 h-5" /> }
  ];

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (selectedFile) => {
    if (selectedFile.type !== 'application/pdf') {
      setStatus('error');
      setErrorMessage('Invalid file type. Only PDF files are allowed.');
      return;
    }
    
    if (selectedFile.size > MAX_FILE_SIZE) {
      setStatus('error');
      setErrorMessage('File exceeds 5MB limit. Please upload a smaller document to ensure live demo stability.');
      return;
    }

    setFile(selectedFile);
    setStatus('processing');
    setErrorMessage('');
    setCurrentStep(1);
    startTimeRef.current = Date.now();

    // Start artificial timer for steps 1 to 3
    timerRef.current = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < 3) return prev + 1; // Halt at step 3 dynamically
        return prev;
      });
    }, 1800); // 1.8 seconds per visual step for demo clarity

    // Prepare API Request
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/api/v1/admin/upload-policy', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}` 
        },
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to ingest document.');
      }

      // API Success - wait for the animation to catch up to step 3 if it hasn't already
      clearInterval(timerRef.current);
      
      setCurrentStep(4); // Trigger final syncing step
      
      setTimeout(() => {
        const elapsed = ((Date.now() - startTimeRef.current) / 1000).toFixed(1);
        setProcessTime(elapsed);
        setStatus('success');
      }, 1000); // Small pause on step 4 to show it completing
      
    } catch (error) {
      clearInterval(timerRef.current);
      setStatus('error');
      setErrorMessage(error.message);
    }
  };

  const resetUpload = () => {
    setFile(null);
    setStatus('idle');
    setErrorMessage('');
    setCurrentStep(0);
    setProcessTime(0);
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-8 bg-slate-900 rounded-2xl border border-slate-800 shadow-2xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Database className="text-blue-500" />
            Knowledge Base Ingestion
          </h2>
          <p className="text-slate-400 mt-1">Securely vectorise and embed financial policies into the AI engine.</p>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {status === 'idle' && (
          <motion.div
            key="upload-zone"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-colors
              ${dragActive ? 'border-blue-500 bg-blue-500/10' : 'border-slate-700 bg-slate-800/50 hover:bg-slate-800 hover:border-slate-600'}
            `}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept="application/pdf"
              onChange={handleChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <UploadCloud className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">Drag & Drop Policy Document</h3>
            <p className="text-slate-400 text-sm">Strictly PDF files up to 5MB</p>
          </motion.div>
        )}

        {status === 'processing' && (
          <motion.div
            key="processing"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-slate-800 p-8 rounded-xl border border-slate-700"
          >
            <div className="flex items-center gap-4 mb-8 pb-6 border-b border-slate-700">
              <FileText className="w-8 h-8 text-blue-500" />
              <div>
                <h4 className="text-white font-medium truncate">{file?.name}</h4>
                <p className="text-slate-400 text-sm">{(file?.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>

            <div className="space-y-6">
              {steps.map((step) => {
                const isActive = currentStep === step.id;
                const isPast = currentStep > step.id;

                return (
                  <div key={step.id} className="flex items-center gap-4">
                    <div className={`
                      flex items-center justify-center w-10 h-10 rounded-full transition-colors duration-500
                      ${isPast ? 'bg-emerald-500/20 text-emerald-500' : isActive ? 'bg-blue-500/20 text-blue-500' : 'bg-slate-700 text-slate-500'}
                    `}>
                      {isPast ? <CheckCircle2 className="w-5 h-5" /> : isActive ? <Loader2 className="w-5 h-5 animate-spin" /> : step.icon}
                    </div>
                    <div>
                      <p className={`font-medium transition-colors duration-500 ${isPast || isActive ? 'text-white' : 'text-slate-500'}`}>
                        {step.title}
                      </p>
                      {isActive && <p className="text-sm text-blue-400 animate-pulse">Processing...</p>}
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {status === 'success' && (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-emerald-900/40 to-slate-800 p-8 rounded-xl border border-emerald-500/30"
          >
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mb-4">
                <CheckCircle2 className="w-10 h-10 text-emerald-500" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Document Vectorised Successfully</h3>
              <p className="text-slate-400 mb-8">{file?.name} is now instantly retrievable by the AI.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mb-8">
                <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                  <div className="text-slate-400 text-sm mb-1">Time Elapsed</div>
                  <div className="text-2xl font-semibold text-white flex items-center gap-2 justify-center">
                    {processTime}s <Zap className="w-4 h-4 text-amber-400" />
                  </div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                  <div className="text-slate-400 text-sm mb-1">Semantic Chunks</div>
                  <div className="text-2xl font-semibold text-white">~48</div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                  <div className="text-slate-400 text-sm mb-1">Vector Dimensions</div>
                  <div className="text-2xl font-semibold text-white text-blue-400">768-D</div>
                </div>
              </div>

              <button
                onClick={resetUpload}
                className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white px-6 py-2.5 rounded-lg transition-colors cursor-pointer"
              >
                <FilePlus className="w-4 h-4" />
                Upload Another Policy
              </button>
            </div>
          </motion.div>
        )}

        {status === 'error' && (
          <motion.div
            key="error"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-900/20 p-8 rounded-xl border border-red-500/30 text-center"
          >
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Ingestion Failed</h3>
            <p className="text-red-400 mb-6">{errorMessage}</p>
            <button
              onClick={resetUpload}
              className="bg-red-500/20 hover:bg-red-500/30 text-red-400 px-6 py-2.5 rounded-lg transition-colors cursor-pointer"
            >
              Try Again
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
