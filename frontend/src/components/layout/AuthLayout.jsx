import React from 'react';

const AuthLayout = ({ children, title, description }) => {
  return (
    <div className="flex min-h-screen w-full bg-gray-50">
      {/* الجانب الأيمن (النموذج) */}
      <div className="flex flex-col justify-center items-center w-full lg:w-1/2 p-8 lg:p-16">
        <div className="w-full max-w-md">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
            <p className="text-gray-600 mt-2">{description}</p>
          </div>
          {children}
        </div>
      </div>

      {/* الجانب الأيسر (الصورة والرسالة التسويقية) */}
      <div className="hidden lg:flex flex-col justify-center items-center w-1/2 bg-brand-primary p-16 text-white">
        <div className="max-w-lg text-center">
          <h2 className="text-4xl font-bold mb-6">Revolutionizing Credit with AI</h2>
          <p className="text-xl opacity-90 leading-relaxed">
            Empowering everyone to access financial opportunities through alternative data-driven credit scoring.
          </p>
          {/* Placeholder لرسوم توضيحية أو صور */}
          <div className="mt-12 w-full h-64 bg-blue-800 rounded-2xl flex items-center justify-center shadow-2xl">
             <span className="text-blue-300">AI Scoring Visualization Placeholder</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
