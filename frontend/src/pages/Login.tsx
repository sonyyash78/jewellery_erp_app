import { useState, useEffect } from 'react';
import { getErrorMessage } from '../utils/errorUtils';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { axiosClient } from '../api/axiosClient';
import toast from 'react-hot-toast';
import { GoogleLogin } from '@react-oauth/google';
import { ShieldCheck, ArrowLeft, Mail, CheckCircle2 } from 'lucide-react';

export default function Login() {
  const [authMode, setAuthMode] = useState<'login' | 'register' | 'forgot'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [resetSent, setResetSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const setAuth = useAuthStore(state => state.setAuth);
  const navigate = useNavigate();

  // Detect offline desktop app environment
  const isElectron = typeof window !== 'undefined' && Boolean(
    (window as any).electronAPI ||
    window.navigator.userAgent.includes('Electron') ||
    window.location.protocol === 'file:'
  );

  // Handle standard email/password login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanId = email.trim().toLowerCase();
    const cleanPassword = password.trim();

    if (!cleanId) {
      toast.error('Please enter your email or username.');
      return;
    }
    if (!cleanPassword) {
      toast.error('Please enter your password.');
      return;
    }

    setLoading(true);
    try {
      const response = await axiosClient.post('/auth/login', {
        username: cleanId,
        password: cleanPassword
      });
      
      const { access_token } = response.data;
      
      // Fetch user profile
      const userRes = await axiosClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      
      const userData = userRes.data;
      setAuth(access_token, userData);
      toast.success('Login successful!');
      const isOwner = userData?.is_owner !== false;
      const mods: string[] = Array.isArray(userData?.allowed_modules) ? userData.allowed_modules : [];
      if (!isOwner && mods.length > 0 && !mods.includes('dashboard')) {
        const routeMap: Record<string, string> = {
          billing: '/billing',
          invoices: '/invoices',
          exchange: '/exchange',
          customers: '/customers',
          inventory: '/inventory',
          purchases: '/purchases',
          reports: '/reports',
          settings: '/settings',
        };
        navigate(routeMap[mods[0]] || '/billing');
      } else {
        navigate('/');
      }
    } catch (error: any) {
      toast.error(getErrorMessage(error, 'Login failed. Please check your credentials.'));
    } finally {
      setLoading(false);
    }
  };

  // Secure Request Password Reset Flow (sends single-use 15m token link via email)
  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanId = email.trim().toLowerCase();

    if (!cleanId) {
      toast.error('Please enter your email address or username.');
      return;
    }

    setLoading(true);
    try {
      const res = await axiosClient.post('/auth/forgot-password', {
        email: cleanId
      });
      toast.success(res.data.message || 'If an account exists, reset instructions have been sent.');
      setResetSent(true);
    } catch (error: any) {
      toast.error(getErrorMessage(error, 'Unable to process reset request. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  // Handle Google Sign-In & Sign-Up
  const handleGoogleSuccess = async (credentialResponse: any) => {
    setLoading(true);
    try {
      const response = await axiosClient.post('/auth/google-login', {
        token: credentialResponse.credential
      });
      
      const { access_token } = response.data;
      
      // Fetch user profile
      const userRes = await axiosClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      
      setAuth(access_token, userRes.data);
      toast.success('Google authentication successful!');
      navigate('/');
    } catch (error: any) {
      toast.error(getErrorMessage(error, 'Google authentication failed.'));
    } finally {
      setLoading(false);
    }
  };

  // Track loading duration to notify user if backend is waking up
  const [loadingTime, setLoadingTime] = useState(0);
  useEffect(() => {
    let timer: any;
    if (loading) {
      timer = setInterval(() => setLoadingTime(t => t + 1), 1000);
    } else {
      setLoadingTime(0);
    }
    return () => clearInterval(timer);
  }, [loading]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-3 sm:p-4">
      <div className="w-full max-w-md bg-surface p-5 sm:p-8 rounded-xl shadow-2xl border border-gray-800 relative overflow-hidden">
        {/* Decorative gold accent */}
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-dark via-primary to-primary-dark"></div>
        
        <h2 className="text-3xl font-bold text-center text-textMain mb-2 uppercase tracking-wide">
          Jewellery <span className="text-primary">ERP</span>
        </h2>
        {isElectron && (
          <div className="flex justify-center mb-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Offline PC Desktop Mode (Local Database)
            </span>
          </div>
        )}
        <p className="text-center text-textMuted mb-6 text-sm">
          {authMode === 'register' 
            ? 'Verified Google Account Registration' 
            : authMode === 'forgot' 
            ? 'Reset Account Password' 
            : 'Secure Portal Access'}
        </p>

        {/* ----------------- REGISTER MODE (ALWAYS REQUIRES GOOGLE) ----------------- */}
        {authMode === 'register' && (
          <div className="space-y-6">
            {isElectron ? (
              <div className="p-4 rounded-xl bg-primary/10 border border-primary/30 text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center mx-auto text-primary">
                  <ShieldCheck size={24} />
                </div>
                <h3 className="text-sm font-bold text-textMain">Offline Store Edition</h3>
                <p className="text-xs text-textMuted leading-relaxed">
                  Your local PC database is pre-initialized with an Administrator account.
                  Sign in with Username <span className="text-primary font-bold">admin</span> and Password <span className="text-primary font-bold">admin</span>. You can manage and add store staff inside Settings.
                </p>
                <button
                  type="button"
                  onClick={() => setAuthMode('login')}
                  className="mt-2 text-xs text-primary hover:underline font-bold"
                >
                  &larr; Back to Sign In
                </button>
              </div>
            ) : (
              <>
                <div className="p-4 rounded-xl bg-primary/10 border border-primary/30 text-center space-y-3">
                  <div className="w-12 h-12 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center mx-auto text-primary">
                    <ShieldCheck size={24} />
                  </div>
                  <h3 className="text-sm font-bold text-textMain">Verified Google Account Required</h3>
                  <p className="text-xs text-textMuted leading-relaxed">
                    To guarantee account ownership and data security, all new store registrations require a verified Google account.
                  </p>
                </div>

                <div className="flex flex-col items-center justify-center pt-2">
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => {
                      toast.error('Google Sign-In failed or was cancelled.');
                    }}
                    text="signup_with"
                    size="large"
                    shape="pill"
                    theme="filled_black"
                  />
                  <p className="text-[11px] text-textMuted text-center mt-3 px-2">
                    Once logged in with Google, you can set your custom username and password inside Settings.
                  </p>
                </div>
              </>
            )}

            <div className="text-center pt-4 border-t border-gray-800">
              <button
                type="button"
                onClick={() => setAuthMode('login')}
                className="text-sm text-primary hover:underline font-medium inline-flex items-center gap-1.5"
              >
                <ArrowLeft size={14} /> Already have an account? Sign In
              </button>
            </div>
          </div>
        )}

        {/* ----------------- FORGOT PASSWORD MODE (SECURE EMAIL LINK FLOW) ----------------- */}
        {authMode === 'forgot' && (
          <div className="space-y-4">
            {resetSent ? (
              <div className="text-center py-4 space-y-4">
                <div className="w-14 h-14 bg-emerald-500/10 border border-emerald-500/30 rounded-full flex items-center justify-center mx-auto text-emerald-400">
                  <CheckCircle2 size={30} />
                </div>
                <h3 className="text-lg font-bold text-textMain">Check Your Inbox</h3>
                <p className="text-xs text-textMuted leading-relaxed px-1">
                  If an account exists for <strong className="text-textMain">{email}</strong>, a secure password reset link has been dispatched.
                </p>
                <div className="p-3 rounded-lg bg-gray-900 border border-gray-800 text-[11px] text-textMuted text-left space-y-1">
                  <p>&bull; The link is single-use and expires in <strong className="text-primary">15 minutes</strong>.</p>
                  <p>&bull; Check your spam or junk folder if you don't receive it shortly.</p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode('login');
                    setResetSent(false);
                    setPassword('');
                  }}
                  className="w-full bg-primary hover:bg-primary-dark text-black font-semibold py-2.5 rounded text-sm transition"
                >
                  Return to Sign In
                </button>
              </div>
            ) : (
              <form onSubmit={handleForgotPassword} className="space-y-4">
                <div className="p-3 rounded-lg bg-gray-900 border border-gray-800 text-xs text-textMuted flex items-start gap-2.5">
                  <Mail size={16} className="text-primary shrink-0 mt-0.5" />
                  <span>
                    Enter your registered email address or username. We will send you a secure password reset link.
                  </span>
                </div>

                <div>
                  <label htmlFor="reset-email" className="block text-sm font-medium text-textMuted mb-1">
                    Email Address or Username
                  </label>
                  <input
                    id="reset-email"
                    type="text"
                    placeholder="you@example.com or username"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-background border border-gray-700 rounded px-4 py-2.5 text-textMain focus:outline-none focus:border-primary transition-colors text-sm"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary hover:bg-primary-dark text-black font-semibold py-2.5 rounded transition-all duration-200 disabled:opacity-50 flex items-center justify-center text-sm shadow-lg shadow-primary/20"
                >
                  <span>{loading ? 'Sending Reset Link...' : 'Send Password Reset Link'}</span>
                </button>

                <div className="text-center mt-3 pt-2 border-t border-gray-800">
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('login');
                      setResetSent(false);
                    }}
                    className="text-sm text-primary hover:underline inline-flex items-center gap-1.5"
                  >
                    <ArrowLeft size={14} /> Back to Sign In
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {/* ----------------- LOGIN MODE ----------------- */}
        {authMode === 'login' && (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="login-id" className="block text-sm font-medium text-textMuted mb-1">Email or Username</label>
              <input 
                id="login-id"
                type="text" 
                placeholder="you@example.com or username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-background border border-gray-700 rounded px-4 py-2.5 text-textMain focus:outline-none focus:border-primary transition-colors text-sm"
                required
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label htmlFor="login-pass" className="block text-sm font-medium text-textMuted">Password</label>
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode('forgot');
                    setPassword('');
                  }}
                  className="text-xs text-primary/80 hover:text-primary transition"
                >
                  Forgot Password?
                </button>
              </div>
              <input 
                id="login-pass"
                type="password" 
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-background border border-gray-700 rounded px-4 py-2.5 text-textMain focus:outline-none focus:border-primary transition-colors text-sm"
                required
              />
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-primary hover:bg-primary-dark text-black font-semibold py-2.5 rounded transition-all duration-200 disabled:opacity-50 flex flex-col items-center justify-center text-sm"
            >
              <span>{loading ? 'Signing In...' : 'Sign In'}</span>
              {loading && loadingTime > 2 && (
                <span className="text-[10px] font-normal text-black/80 mt-0.5 animate-pulse">
                  Connecting to backend ({loadingTime}s)...
                </span>
              )}
            </button>

            {isElectron && (
              <div className="mt-3 p-2.5 rounded-lg bg-surface/50 border border-gray-800 text-center">
                <span className="text-[11px] text-textMuted block">Default Offline Login:</span>
                <span className="text-xs font-mono font-bold text-primary">Username: admin &nbsp;|&nbsp; Password: admin</span>
              </div>
            )}
            
            {!isElectron && (
              <>
                <div className="text-center mt-3">
                  <button 
                    type="button" 
                    onClick={() => setAuthMode('register')} 
                    className="text-sm text-primary hover:underline"
                  >
                    Need an account? Sign Up with Google
                  </button>
                </div>

                <div className="flex items-center justify-center space-x-2 my-4">
                  <div className="h-px bg-gray-700 w-full"></div>
                  <span className="text-textMuted text-xs uppercase tracking-wider">OR</span>
                  <div className="h-px bg-gray-700 w-full"></div>
                </div>
                
                <div className="flex flex-col items-center">
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => {
                      toast.error('Google Sign-In origin not authorized. Please use Email/Password.');
                    }}
                    text="signin_with"
                    size="large"
                    shape="pill"
                    theme="filled_black"
                  />
                  <p className="text-[11px] text-textMuted text-center mt-2 px-1">
                    Fast &amp; secure one-click sign in with your verified Google account.
                  </p>
                </div>
              </>
            )}

            <div className="text-center pt-4 border-t border-gray-800/80 mt-6">
              <button
                type="button"
                onClick={() => navigate('/verify')}
                className="text-xs text-yellow-500/80 hover:text-yellow-400 font-medium inline-flex items-center gap-1.5 transition"
              >
                <span>🔍 Verify Genuine Bill / Certificate</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
