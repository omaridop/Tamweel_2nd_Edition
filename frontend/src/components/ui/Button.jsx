import React from 'react';
import { twMerge } from 'tailwind-merge';

const Button = ({ 
  children, 
  type = 'button', 
  onClick, 
  className, 
  isLoading = false, 
  variant = 'primary', 
  ...props 
}) => {
  const variants = {
    primary: 'bg-primary text-white hover:bg-slate-800 shadow-sm',
    accent: 'bg-accent text-white hover:bg-emerald-600 shadow-sm',
    outline: 'bg-transparent border border-slate-200 text-slate-700 hover:bg-slate-50',
    ghost: 'bg-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900',
    ai: 'bg-ai text-white hover:bg-indigo-600 shadow-md shadow-indigo-100',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={isLoading}
      className={twMerge(
        "inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-sm font-bold transition-all duration-200 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    >
      {isLoading ? (
        <svg className="animate-spin h-4 w-4 mr-2 text-current" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      ) : null}
      {children}
    </button>
  );
};

export default Button;
