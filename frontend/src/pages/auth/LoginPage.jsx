import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { BrainCircuit } from 'lucide-react';
import useAuthStore from '../../store/useAuthStore';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      await login(data.email, data.password);
      // Get the role from the store after login
      const role = useAuthStore.getState().role;
      
      if (role === 'admin' || role === 'sponsor') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch { // setError('Invalid email or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex bg-slate-50">
      {/* Left Side: Form */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center items-center p-8 lg:p-16">
        <div className="w-full max-w-md space-y-8">
          <div className="flex flex-col items-center lg:items-start text-center lg:text-left">
            {/* TAMWEEL Logo Placeholder */}
            <div className="flex items-center mb-8">
              <div className="w-12 h-12 bg-accent rounded-xl flex items-center justify-center mr-4 shadow-lg shadow-emerald-100">
                <span className="font-bold text-white text-2xl">T</span>
              </div>
              <span className="font-extrabold text-3xl tracking-tight text-primary">Tamweel</span>
            </div>
            <h1 className="text-3xl font-extrabold text-primary tracking-tight">Welcome back</h1>
            <p className="text-slate-500 font-medium mt-2">Log in to your account to securely manage your financial data.</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6">
            
            <Input
              label="Email Address"
              type="email"
              placeholder="name@example.com"
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
              {isLoading ? 'Authenticating...' : 'Sign In'}
            </Button>

            <div className="relative py-4">
              <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-slate-200"></span></div>
              <div className="relative flex justify-center text-xs uppercase"><span className="bg-slate-50 px-2 text-slate-400 font-bold">Or continue with</span></div>
            </div>

            <Button variant="outline" className="w-full h-12" type="button">
               <img src="https://www.svgrepo.com/show/355037/google.svg" className="w-5 h-5 mr-2" alt="Google" />
               Google
            </Button>
          </form>

          <p className="text-center text-sm text-slate-500 pt-4">
            New to Tamweel?{' '}
            <Link to="/register" className="text-accent font-bold hover:underline">
              Apply for an account
            </Link>
          </p>
        </div>
      </div>

      {/* Right Side: Branding/Trust */}
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
              

          </div>
      </div>
    </div>
  );
};

export default LoginPage;
