import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  UserCircle, 
  BrainCircuit, 
  Link2, 
  MessageSquareWarning, 
  Settings,
  LogOut,
  Menu,
  X,
  Bell
} from 'lucide-react';
import { twMerge } from 'tailwind-merge';
import useAuthStore from '../store/useAuthStore';
import ChatBot from '../components/ui/ChatBot';

const MainLayout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/user/dashboard', icon: LayoutDashboard, role: 'user' },
    { name: 'AI Simulator', href: '/user/simulator', icon: BrainCircuit, role: 'user' },
    { name: 'Connections', href: '/user/connections', icon: Link2, role: 'user' },
    { name: 'Disputes', href: '/user/disputes', icon: MessageSquareWarning, role: 'user' },
    { name: 'Sponsor Portal', href: '/sponsor/dashboard', icon: UserCircle, role: 'sponsor' },
  ];

  const currentRole = useAuthStore.getState().role || 'user'; // Fallback to user
  const filteredNavigation = navigation.filter(item => 
    item.role === currentRole || (currentRole === 'sponsor' && item.role === 'user') // Sponsor sees everything, user sees only user stuff
  );

  return (
    <div className="min-h-screen bg-bg-subtle flex">
      {/* Sidebar */}
      <aside className={twMerge(
        "bg-primary text-white transition-all duration-300 ease-in-out fixed inset-y-0 left-0 z-50 lg:relative lg:translate-x-0",
        isSidebarOpen ? "w-64 translate-x-0" : "w-20 -translate-x-full lg:translate-x-0"
      )}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="h-16 flex items-center px-6 border-b border-white/10">
            <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center mr-3 shrink-0">
               <span className="font-bold text-white">T</span>
            </div>
            {isSidebarOpen && <span className="font-bold text-xl tracking-tight">Tamweel</span>}
          </div>

          {/* Nav Links */}
          <nav className="flex-1 px-3 py-6 space-y-1 overflow-y-auto">
            {filteredNavigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={twMerge(
                    "flex items-center px-3 py-2.5 rounded-xl transition-all duration-200 group",
                    isActive 
                      ? "bg-accent text-white" 
                      : "text-slate-400 hover:bg-white/5 hover:text-white"
                  )}
                >
                  <item.icon className={twMerge("w-5 h-5 shrink-0", isSidebarOpen && "mr-3")} />
                  {isSidebarOpen && <span className="font-medium">{item.name}</span>}
                </Link>
              );
            })}
          </nav>

          {/* Footer Nav */}
          <div className="px-3 py-6 border-t border-white/10 space-y-1">
             <Link to="/settings" className="flex items-center px-3 py-2.5 rounded-xl text-slate-400 hover:bg-white/5 hover:text-white transition-all">
                <Settings className={twMerge("w-5 h-5 shrink-0", isSidebarOpen && "mr-3")} />
                {isSidebarOpen && <span className="font-medium">Settings</span>}
             </Link>
             <button 
               onClick={handleLogout}
               className="w-full flex items-center px-3 py-2.5 rounded-xl text-red-400 hover:bg-red-500/10 transition-all"
             >
                <LogOut className={twMerge("w-5 h-5 shrink-0", isSidebarOpen && "mr-3")} />
                {isSidebarOpen && <span className="font-medium">Logout</span>}
             </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 lg:px-8 shrink-0">
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 rounded-lg hover:bg-slate-100 text-slate-500 transition-all"
          >
            {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <div className="flex items-center space-x-4 relative">
            <button className="p-2 rounded-lg hover:bg-slate-100 text-slate-500 relative">
               <Bell className="w-5 h-5" />
               <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            </button>
            
            {/* Profile Dropdown Trigger */}
            <div className="relative">
              <button 
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="h-10 w-10 rounded-full bg-slate-200 border border-slate-300 overflow-hidden hover:ring-2 hover:ring-accent transition-all"
              >
                  <img src={`https://ui-avatars.com/api/?name=${user?.name || 'User'}&background=0F172A&color=fff`} alt="User" />
              </button>

              {/* Dropdown Menu */}
              {isProfileOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-10" 
                    onClick={() => setIsProfileOpen(false)}
                  ></div>
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-xl border border-slate-100 py-2 z-20 animate-in fade-in zoom-in-95 duration-200 origin-top-right">
                    <div className="px-4 py-3 border-b border-slate-50">
                      <p className="text-sm font-bold text-primary">{user?.name || 'Anas'}</p>
                      <p className="text-xs text-slate-500 font-medium">{user?.email || 'anas@tamweel.ai'}</p>
                    </div>
                    
                    <div className="py-1">
                      <button className="w-full flex items-center px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 transition-all">
                        <UserCircle className="w-4 h-4 mr-3 text-slate-400" />
                        Profile Status
                        <span className="ml-auto px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 text-[10px] font-bold">Verified</span>
                      </button>
                      <Link to="/settings" className="flex items-center px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 transition-all">
                        <Settings className="w-4 h-4 mr-3 text-slate-400" />
                        Account Settings
                      </Link>
                    </div>

                    <div className="py-1 border-t border-slate-50">
                      <button 
                        onClick={handleLogout}
                        className="w-full flex items-center px-4 py-2.5 text-sm text-red-500 hover:bg-red-50 transition-all font-medium"
                      >
                        <LogOut className="w-4 h-4 mr-3" />
                        Sign Out
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
           {children}
        </main>
      </div>

      <ChatBot />
    </div>
  );
};

export default MainLayout;
