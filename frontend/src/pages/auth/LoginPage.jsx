import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { BrainCircuit, ShieldCheck } from 'lucide-react';
import useAuthStore from '../../store/useAuthStore';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid business email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    setError('');
    try {
      await login(data.email, data.password);
      // Get the role from the store after login
      const role = useAuthStore.getState().role;
      
      if (role === 'sponsor') {
        navigate('/sponsor/dashboard');
      } else {
        navigate('/user/dashboard');
      }
    } catch (err) {
      setError('Invalid email or password. Please use the provided credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex bg-slate-50">
      {/* Right Side: Form */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center items-center p-8 lg:p-16">
        <div className="w-full max-w-md space-y-8">
          <div className="flex flex-col items-center lg:items-start text-center lg:text-left">
            <div className="w-12 h-12 bg-accent rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-emerald-100">
               <ShieldCheck className="text-white w-7 h-7" />
            </div>
            <h1 className="text-3xl font-extrabold text-primary tracking-tight">Institutional Access</h1>
            <p className="text-slate-500 font-medium mt-2">Securely manage your AI-driven credit assessment.</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-10 space-y-6">
            {error && (
              <div className="p-4 bg-red-50 border border-red-100 text-red-600 rounded-xl text-sm font-medium animate-in fade-in slide-in-from-top-1">
                {error}
              </div>
            )}
            
            <Input
              label="Business Email"
              type="email"
              placeholder="anas@tamweel.ai"
              error={errors.email?.message}
              {...register('email')}
            />

            <div className="space-y-1">
              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                error={errors.password?.message}
                {...register('password')}
              />
              <div className="flex justify-end">
                <button type="button" className="text-xs font-bold text-accent hover:underline">
                  Forgot Password?
                </button>
              </div>
            </div>

            <Button type="submit" className="w-full h-12" isLoading={isLoading} variant="primary">
              Sign In to Dashboard
            </Button>

            <div className="relative py-4">
              <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-slate-200"></span></div>
              <div className="relative flex justify-center text-xs uppercase"><span className="bg-slate-50 px-2 text-slate-400 font-bold">Or continue with</span></div>
            </div>

            <Button variant="outline" className="w-full h-12">
               <img src="https://www.svgrepo.com/show/355037/google.svg" className="w-5 h-5 mr-2" alt="Google" />
               Google Workspace
            </Button>
          </form>

          <p className="text-center text-sm text-slate-500">
            New to Tamweel?{' '}
            <Link to="/register" className="text-accent font-bold hover:underline">
              Apply for an account
            </Link>
          </p>
        </div>
      </div>

      {/* Left Side: Branding/Trust */}
      <div className="hidden lg:flex w-1/2 bg-primary relative overflow-hidden flex-col justify-center p-20 text-white">
          <div className="absolute top-0 left-0 w-full h-full opacity-10">
              <div className="absolute -top-24 -left-24 w-96 h-96 bg-accent rounded-full blur-3xl"></div>
              <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-ai rounded-full blur-3xl"></div>
          </div>
          
          <div className="relative z-10 space-y-12">
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/10 text-accent text-sm font-bold">
                  <BrainCircuit className="w-4 h-4 mr-2" />
                  Explainable AI (XAI) Integrated
              </div>
              
              <h2 className="text-5xl font-bold leading-tight">
                Transparent credit <br /> 
                <span className="text-accent underline decoration-accent/30 decoration-8 underline-offset-8">assessment</span> for the next billion.
              </h2>
              
              <div className="grid grid-cols-2 gap-8 pt-8">
                  <div>
                      <p className="text-3xl font-bold">99.9%</p>
                      <p className="text-slate-400 text-sm font-medium">Data Integrity</p>
                  </div>
                  <div>
                      <p className="text-3xl font-bold">1.2M+</p>
                      <p className="text-slate-400 text-sm font-medium">Assessments Run</p>
                  </div>
              </div>

              <div className="pt-12">
                  <div className="glass p-6 rounded-2xl max-w-sm">
                      <p className="text-slate-200 text-sm italic mb-4">
                        "Tamweel's AI insights helped us identify creditworthy borrowers we would have otherwise missed."
                      </p>
                      <div className="flex items-center">
                          <div className="w-10 h-10 rounded-full bg-slate-700 mr-3"></div>
                          <div>
                              <p className="text-xs font-bold">Sarah Chen</p>
                              <p className="text-[10px] text-slate-400 uppercase tracking-wider">CTO @ FinBank</p>
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      </div>
    </div>
  );
};

export default LoginPage;
