import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { axiosClient } from '../api/axiosClient';
import { getErrorMessage } from '../utils/errorUtils';
import toast from 'react-hot-toast';
import { Lock, CheckCircle2, AlertTriangle, ArrowLeft, KeyRound } from 'lucide-react';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const navigate = useNavigate();

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState<boolean | null>(null);
  const [tokenError, setTokenError] = useState('');
  const [success, setSuccess] = useState(false);

  // Validate token upon loading page
  useEffect(() => {
    if (!token) {
      setVerifying(false);
      setTokenValid(false);
      setTokenError('No password reset token was provided in the URL.');
      return;
    }

    const checkToken = async () => {
      try {
        await axiosClient.get('/auth/verify-reset-token', {
          params: { token }
        });
        setTokenValid(true);
      } catch (err: any) {
        setTokenValid(false);
        setTokenError(
          getErrorMessage(
            err,
            'This password reset link is invalid, expired (15-minute limit), or has already been used.'
          )
        );
      } finally {
        setVerifying(false);
      }
    };

    checkToken();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanPwd = password;
    const cleanConfirm = confirmPassword;

    if (!token) {
      toast.error('Missing reset token. Please request a new password reset email.');
      return;
    }

    if (cleanPwd.length < 8) {
      toast.error('Password must be at least 8 characters long.');
      return;
    }

    if (cleanPwd !== cleanConfirm) {
      toast.error('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const response = await axiosClient.post('/auth/reset-password', {
        token: token.trim(),
        new_password: cleanPwd,
        confirm_password: cleanConfirm
      });

      toast.success(response.data.message || 'Password updated successfully!');
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2500);
    } catch (err: any) {
      toast.error(getErrorMessage(err, 'Failed to reset password. Token may be invalid or expired.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-3 sm:p-4">
      <div className="w-full max-w-md bg-surface p-5 sm:p-8 rounded-xl shadow-2xl border border-gray-800 relative overflow-hidden">
        {/* Decorative gold accent */}
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-dark via-primary to-primary-dark"></div>

        <h2 className="text-3xl font-bold text-center text-textMain mb-2 uppercase tracking-wide">
          Jewellery <span className="text-primary">ERP</span>
        </h2>
        <p className="text-center text-textMuted mb-6 text-sm">
          Set New Account Password
        </p>

        {verifying ? (
          <div className="text-center py-8 space-y-3">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-sm text-textMuted">Verifying security token...</p>
          </div>
        ) : success ? (
          <div className="text-center py-6 space-y-4">
            <div className="w-14 h-14 bg-emerald-500/10 border border-emerald-500/30 rounded-full flex items-center justify-center mx-auto text-emerald-400">
              <CheckCircle2 size={32} />
            </div>
            <h3 className="text-lg font-bold text-textMain">Password Reset Complete!</h3>
            <p className="text-xs text-textMuted leading-relaxed">
              Your password has been securely updated. Redirecting you to sign in...
            </p>
            <Link
              to="/login"
              className="inline-block w-full py-2.5 px-4 bg-primary hover:bg-primary-dark text-black font-semibold rounded text-sm transition"
            >
              Sign In Now
            </Link>
          </div>
        ) : !tokenValid ? (
          <div className="text-center py-6 space-y-4">
            <div className="w-14 h-14 bg-rose-500/10 border border-rose-500/30 rounded-full flex items-center justify-center mx-auto text-rose-400">
              <AlertTriangle size={30} />
            </div>
            <h3 className="text-lg font-bold text-textMain">Invalid or Expired Link</h3>
            <p className="text-xs text-textMuted leading-relaxed px-2">
              {tokenError || 'This password reset link is invalid or has expired. For your security, reset links are single-use and expire after 15 minutes.'}
            </p>
            <div className="pt-2">
              <Link
                to="/login"
                className="inline-flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-primary hover:bg-primary-dark text-black font-semibold rounded text-sm transition"
              >
                <ArrowLeft size={16} /> Request a New Reset Link
              </Link>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="p-3 rounded-lg bg-gray-900 border border-gray-800 text-xs text-textMuted flex items-start gap-2.5">
              <KeyRound size={16} className="text-primary shrink-0 mt-0.5" />
              <span>
                Please enter a strong new password (minimum 8 characters). This token is single-use and will be invalidated once submitted.
              </span>
            </div>

            <div>
              <label htmlFor="new-pass" className="block text-sm font-medium text-textMuted mb-1">
                New Password
              </label>
              <div className="relative">
                <input
                  id="new-pass"
                  type="password"
                  placeholder="Minimum 8 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-background border border-gray-700 rounded px-4 py-2.5 text-textMain focus:outline-none focus:border-primary transition-colors text-sm pr-10"
                  required
                  minLength={8}
                />
                <Lock size={16} className="absolute right-3 top-3 text-gray-500" />
              </div>
              {password.length > 0 && password.length < 8 && (
                <p className="text-[11px] text-rose-400 mt-1">Must be at least 8 characters ({password.length}/8)</p>
              )}
            </div>

            <div>
              <label htmlFor="confirm-pass" className="block text-sm font-medium text-textMuted mb-1">
                Confirm New Password
              </label>
              <div className="relative">
                <input
                  id="confirm-pass"
                  type="password"
                  placeholder="Re-enter your new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full bg-background border border-gray-700 rounded px-4 py-2.5 text-textMain focus:outline-none focus:border-primary transition-colors text-sm pr-10"
                  required
                  minLength={8}
                />
                <Lock size={16} className="absolute right-3 top-3 text-gray-500" />
              </div>
              {confirmPassword.length > 0 && confirmPassword !== password && (
                <p className="text-[11px] text-rose-400 mt-1">Passwords do not match</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || password.length < 8 || password !== confirmPassword}
              className="w-full bg-primary hover:bg-primary-dark text-black font-semibold py-2.5 rounded transition-all duration-200 disabled:opacity-50 flex items-center justify-center text-sm shadow-lg shadow-primary/20"
            >
              <span>{loading ? 'Securing Password...' : 'Save New Password'}</span>
            </button>

            <div className="text-center mt-3 pt-2 border-t border-gray-800">
              <Link
                to="/login"
                className="text-xs text-primary hover:underline inline-flex items-center gap-1.5"
              >
                <ArrowLeft size={12} /> Back to Sign In
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
