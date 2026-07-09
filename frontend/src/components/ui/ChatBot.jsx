import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { MessageSquare, X } from 'lucide-react';
import { twMerge } from 'tailwind-merge';
import { RAGChatWidget } from '../chat/RAGChatWidget';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleOpenChat = () => setIsOpen(true);
    window.addEventListener('open-chat', handleOpenChat);
    return () => window.removeEventListener('open-chat', handleOpenChat);
  }, []);

  const isAuthPage = location.pathname.includes('/login') || location.pathname.includes('/register');

  if (isAuthPage) return null;

  return (
    <div className="fixed bottom-6 right-6 z-[100]">
      {/* Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={twMerge(
          "w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 active:scale-95",
          isOpen ? "bg-slate-800 rotate-90" : "bg-accent hover:bg-emerald-600"
        )}
      >
        {isOpen ? <X className="text-white w-6 h-6" /> : <MessageSquare className="text-white w-6 h-6" />}
      </button>

      {/* Chat Window */}
      <div 
        className={twMerge(
          "absolute bottom-20 right-0 w-[350px] md:w-[450px] h-[600px] bg-[#0b1120] rounded-3xl shadow-2xl overflow-hidden transition-all duration-300",
          isOpen ? "opacity-100 scale-100 visible" : "opacity-0 scale-95 invisible pointer-events-none"
        )}
        style={{ transformOrigin: "bottom right" }}
      >
        <RAGChatWidget onClose={() => setIsOpen(false)} />
      </div>
    </div>
  );
};

export default ChatBot;
