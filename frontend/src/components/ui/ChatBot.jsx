import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Loader2 } from 'lucide-react';
import { twMerge } from 'tailwind-merge';
import { scoringService } from '../../services/api';
import useAuthStore from '../../store/useAuthStore';
import Button from './Button';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Hello! I am Tamweel AI. How can I help you understand your credit score today?' }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const { user, role } = useAuthStore();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const userMsg = message.trim();
    setMessage('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setIsLoading(true);

    try {
      const response = await scoringService.chat(user?.name || 'Anas', userMsg, role || 'user');
      setMessages(prev => [...prev, { role: 'ai', text: response.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', text: 'Sorry, I am having trouble connecting. Please try again later.' }]);
    } finally {
      setIsLoading(false);
    }
  };

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
      {isOpen && (
        <div className="absolute bottom-20 right-0 w-[350px] md:w-[400px] h-[500px] bg-white rounded-3xl shadow-2xl border border-slate-100 flex flex-col overflow-hidden animate-in slide-in-from-bottom-5 duration-300">
          {/* Header */}
          <div className="p-6 bg-primary text-white flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center">
                <Bot className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-sm">{role === 'sponsor' ? 'Portfolio Analyst AI' : 'Tamweel AI Assistant'}</h3>
                <p className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider">Online</p>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-white/50 hover:text-white transition-all">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={twMerge(
                  "flex items-start gap-3",
                  msg.role === 'user' ? "flex-row-reverse" : ""
                )}
              >
                <div className={twMerge(
                  "w-8 h-8 rounded-lg flex items-center justify-center shrink-0",
                  msg.role === 'ai' ? "bg-indigo-100 text-indigo-600" : "bg-slate-200 text-slate-600"
                )}>
                  {msg.role === 'ai' ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                </div>
                <div className={twMerge(
                  "p-3 rounded-2xl text-sm leading-relaxed max-w-[80%]",
                  msg.role === 'ai' 
                    ? "bg-white border border-slate-100 text-slate-700 shadow-sm rounded-tl-none" 
                    : "bg-primary text-white rounded-tr-none"
                )}>
                  {msg.text}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
                  <Bot className="w-5 h-5" />
                </div>
                <div className="bg-white border border-slate-100 p-3 rounded-2xl rounded-tl-none shadow-sm">
                  <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSend} className="p-4 bg-white border-t border-slate-100 flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask about your score..."
              className="flex-1 bg-slate-50 border-none rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-accent transition-all"
            />
            <button
              type="submit"
              disabled={!message.trim() || isLoading}
              className="w-10 h-10 bg-accent text-white rounded-xl flex items-center justify-center hover:bg-emerald-600 disabled:opacity-50 transition-all"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default ChatBot;
