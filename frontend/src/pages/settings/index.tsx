import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { axiosClient } from '../../api/axiosClient';
import { useAuthStore } from '../../store/authStore';
import { Save, Upload, Download, ShieldCheck, Database, Building2, KeyRound, Users } from 'lucide-react';
import { getErrorMessage } from '../../utils/errorUtils';
import { BACKEND_BASE_URL } from '../../config/api';
import toast from 'react-hot-toast';
import StaffAccessPanel from './StaffAccessPanel';

export default function SettingsModule() {
  const [searchParams] = useSearchParams();
  const tabParam = searchParams.get('tab');
  const [activeTab, setActiveTab] = useState(tabParam || 'profile');

  useEffect(() => {
    if (tabParam) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [logoTimestamp, setLogoTimestamp] = useState<number>(Date.now());
  const user = useAuthStore(state => state.user);
  const storeName = user?.store?.name || settings.business_name || settings.store_name || 'My Store';
  const storeSlug = storeName.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase();

  // User Credentials state (custom username & password for Google users)
  const [credUsername, setCredUsername] = useState('');
  const [credFullName, setCredFullName] = useState('');
  const [credCurrentPassword, setCredCurrentPassword] = useState('');
  const [credPassword, setCredPassword] = useState('');
  const [credConfirmPassword, setCredConfirmPassword] = useState('');
  const [credLoading, setCredLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setCredUsername(user.username || '');
      setCredFullName(user.full_name || '');
    }
  }, [user]);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const res = await axiosClient.get('/settings/');
      setSettings(res.data);
      setLogoTimestamp(Date.now());
    } catch (e) {
      toast.error('Failed to load settings');
    }
  };

  const syncUserStore = async () => {
    try {
      const userRes = await axiosClient.get('/auth/me');
      const token = useAuthStore.getState().token;
      if (token && userRes.data) {
        useAuthStore.getState().setAuth(token, userRes.data);
      }
    } catch (err) {
      console.error('Failed to sync authStore after settings update', err);
    }
  };

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    if (logoFile) {
      await handleLogoUpload();
    }
    const filteredPayload = Object.entries(settings)
      .filter(([key]) => !key.match(/^store_\d+_/))
      .map(([key, value]) => ({ key, value }));
    try {
      const res = await axiosClient.post('/settings/', filteredPayload);
      toast.success('Settings saved successfully');
      
      const newName = res.data?.store_name || res.data?.business_name || settings['business_name'] || settings['store_name'];
      const newLogo = res.data?.logo_url || settings['logo_url'];
      useAuthStore.getState().updateUser({
        store_name: newName,
        logo_url: newLogo
      });
      window.dispatchEvent(new Event('settings-updated'));

      await fetchSettings();
      await syncUserStore();
    } catch (e) {
      toast.error('Failed to save settings');
    }
  };

  const handleLogoUpload = async (customFile?: File) => {
    const fileToUpload = customFile || logoFile;
    if (!fileToUpload) return;
    const formData = new FormData();
    formData.append('file', fileToUpload);
    try {
      toast.loading('Uploading logo...', { id: 'logo-up' });
      const uploadRes = await axiosClient.post('/settings/logo', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Logo uploaded and updated successfully!', { id: 'logo-up' });
      setLogoFile(null);
      setPreviewUrl(null);
      const newLogoUrl = uploadRes.data?.url || settings['logo_url'];
      setLogoTimestamp(Date.now());
      setSettings(prev => ({ ...prev, logo_url: newLogoUrl }));
      
      useAuthStore.getState().updateUser({
        logo_url: newLogoUrl
      });
      window.dispatchEvent(new Event('settings-updated'));

      await fetchSettings();
      await syncUserStore();
    } catch (e) {
      toast.error('Failed to upload logo', { id: 'logo-up' });
    }
  };

  const handleSaveCredentials = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanUsername = credUsername.trim();
    const cleanCurrentPassword = credCurrentPassword;
    const cleanPassword = credPassword;
    const cleanFullName = credFullName.trim();

    if (cleanUsername && cleanUsername.length < 3) {
      toast.error('Username must be at least 3 characters long.');
      return;
    }

    if (cleanPassword) {
      if (cleanPassword.length < 8) {
        toast.error('Password must be at least 8 characters long.');
        return;
      }
      if (cleanPassword !== credConfirmPassword) {
        toast.error('Passwords do not match.');
        return;
      }
    }

    if (!cleanUsername && !cleanPassword && !cleanFullName) {
      toast.error('Please enter a username or password to update.');
      return;
    }

    setCredLoading(true);
    try {
      const res = await axiosClient.post('/auth/set-credentials', {
        username: cleanUsername || undefined,
        current_password: cleanCurrentPassword || undefined,
        password: cleanPassword || undefined,
        full_name: cleanFullName || undefined
      });

      toast.success(res.data.message || 'Credentials updated successfully!');
      setCredCurrentPassword('');
      setCredPassword('');
      setCredConfirmPassword('');

      // Refresh user profile
      const userRes = await axiosClient.get('/auth/me');
      if (userRes.data) {
        useAuthStore.getState().setAuth(useAuthStore.getState().token!, userRes.data);
      }
    } catch (err: any) {
      toast.error(getErrorMessage(err, 'Failed to update credentials.'));
    } finally {
      setCredLoading(false);
    }
  };

  const handleBackup = async () => {
    try {
      toast.loading('Generating store SQL backup...', { id: 'bk-sql' });
      const response = await axiosClient.get('/backup/download', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${storeSlug}_sql_backup_${new Date().toISOString().slice(0,10)}.sql.enc`);
      document.body.appendChild(link);
      link.click();
      toast.success(`${storeName} Encrypted SQL backup downloaded!`, { id: 'bk-sql' });
    } catch (e) {
      toast.error('SQL Backup download failed', { id: 'bk-sql' });
    }
  };

  const handleSingleExcelBackup = async () => {
    try {
      toast.loading('Exporting store tables to Master Excel...', { id: 'bk-excel' });
      const response = await axiosClient.get('/backup/all-tables-excel', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${storeSlug}_master_backup_${new Date().toISOString().slice(0,10)}.xlsx`);
      document.body.appendChild(link);
      link.click();
      toast.success(`${storeName} Master Excel downloaded!`, { id: 'bk-excel' });
    } catch (e) {
      toast.error('Master Excel export failed', { id: 'bk-excel' });
    }
  };

  const handleExcelBackup = async () => {
    try {
      toast.loading('Packaging Excel tables into ZIP archive...', { id: 'bk-zip' });
      const response = await axiosClient.get('/backup/excel-download', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${storeSlug}_tables_archive_${new Date().toISOString().slice(0,10)}.zip`);
      document.body.appendChild(link);
      link.click();
      toast.success(`${storeName} Excel archive downloaded!`, { id: 'bk-zip' });
    } catch (e) {
      toast.error('Excel backup failed', { id: 'bk-zip' });
    }
  };

  return (
    <div className="h-auto lg:h-[calc(100vh-6rem)] flex flex-col lg:flex-row gap-4 overflow-y-auto lg:overflow-hidden">
      
      {/* Sidebar */}
      <div className="w-full lg:w-64 bg-surface border border-gray-800 rounded-xl shadow-lg flex flex-row lg:flex-col p-2 sm:p-4 shrink-0 overflow-x-auto lg:overflow-y-auto custom-scrollbar">
        <h2 className="hidden lg:block text-primary font-bold uppercase tracking-widest text-sm mb-6 border-b border-gray-800 pb-4 shrink-0">Settings</h2>
        
        <div className="flex lg:flex-col gap-2 w-full whitespace-nowrap">
          <button 
            onClick={() => setActiveTab('profile')} 
            className={`shrink-0 lg:w-full flex items-center gap-2 lg:gap-3 px-3 lg:px-4 py-2 lg:py-3 rounded-lg text-left transition-colors font-bold text-xs sm:text-sm ${activeTab === 'profile' ? 'bg-primary/20 text-primary border border-primary/30' : 'text-textMuted hover:bg-gray-800'}`}
          >
            <Building2 size={18} /> Business Profile
          </button>
          
          <button 
            onClick={() => setActiveTab('security')} 
            className={`shrink-0 lg:w-full flex items-center gap-2 lg:gap-3 px-3 lg:px-4 py-2 lg:py-3 rounded-lg text-left transition-colors font-bold text-xs sm:text-sm ${activeTab === 'security' ? 'bg-primary/20 text-primary border border-primary/30' : 'text-textMuted hover:bg-gray-800'}`}
          >
            <ShieldCheck size={18} /> Account &amp; Security
          </button>
          
          {user?.is_owner !== false && (
            <button 
              onClick={() => setActiveTab('staff')} 
              className={`shrink-0 lg:w-full flex items-center gap-2 lg:gap-3 px-3 lg:px-4 py-2 lg:py-3 rounded-lg text-left transition-colors font-bold text-xs sm:text-sm ${activeTab === 'staff' ? 'bg-primary/20 text-primary border border-primary/30' : 'text-textMuted hover:bg-gray-800'}`}
            >
              <Users size={18} /> Staff &amp; Access
            </button>
          )}

          <button 
            onClick={() => setActiveTab('database')} 
            className={`shrink-0 lg:w-full flex items-center gap-2 lg:gap-3 px-3 lg:px-4 py-2 lg:py-3 rounded-lg text-left transition-colors font-bold text-xs sm:text-sm ${activeTab === 'database' ? 'bg-primary/20 text-primary border border-primary/30' : 'text-textMuted hover:bg-gray-800'}`}
          >
            <Database size={18} /> Store Data &amp; Backup
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 bg-surface border border-gray-800 rounded-xl shadow-lg overflow-y-auto p-4 sm:p-8 custom-scrollbar">
        
        {activeTab === 'staff' && user?.is_owner !== false && (
          <StaffAccessPanel />
        )}

        {activeTab === 'profile' && (
          <div className="max-w-2xl">
            <h2 className="text-2xl font-bold text-textMain mb-6">Business Profile</h2>
            
            <div className="mb-6 sm:mb-8 p-4 sm:p-6 border border-gray-800 rounded-xl bg-black/20">
              <h3 className="text-sm font-bold text-primary uppercase mb-4">Shop Logo</h3>
              <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4 sm:gap-6">
                <div className="w-24 h-24 bg-gray-900 border border-gray-700 rounded-lg flex items-center justify-center overflow-hidden shrink-0">
                  <img 
                    key={`${settings['logo_url']}-${logoTimestamp}-${previewUrl}`}
                    src={
                      previewUrl 
                        ? previewUrl
                        : (settings['logo_url'] 
                            ? (settings['logo_url'].startsWith('http') 
                                ? `${settings['logo_url']}?v=${logoTimestamp}` 
                                : `${BACKEND_BASE_URL}${settings['logo_url'].startsWith('/') ? '' : '/'}${settings['logo_url']}?v=${logoTimestamp}`)
                            : `${BACKEND_BASE_URL}/static/logo.png?v=${logoTimestamp}`)
                    } 
                    alt="Logo" 
                    className="max-w-full max-h-full object-contain" 
                    onError={(e) => (e.currentTarget.style.display = 'none')} 
                  />
                </div>
                <div className="flex-1">
                  <input 
                    type="file" 
                    accept="image/png, image/jpeg" 
                    onChange={async (e) => {
                      const file = e.target.files?.[0] || null;
                      setLogoFile(file);
                      if (file) {
                        setPreviewUrl(URL.createObjectURL(file));
                        await handleLogoUpload(file);
                      } else {
                        setPreviewUrl(null);
                      }
                    }} 
                    className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-black hover:file:bg-primary-dark mb-4" 
                  />
                  <button 
                    type="button"
                    onClick={() => handleLogoUpload()} 
                    className="bg-background border border-gray-700 hover:border-primary text-textMain px-4 py-2 rounded text-sm font-bold transition-colors flex items-center gap-2"
                  >
                    <Upload size={16} /> Upload Logo
                  </button>
                </div>
              </div>
            </div>

            <form onSubmit={handleSaveSettings} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Business Name</label>
                  <input 
                    value={settings['business_name'] || ''} 
                    onChange={e => {
                      const val = e.target.value;
                      const oldName = settings['business_name'] || '';
                      const currentUpi = settings['upi_name'] || '';
                      const newSettings: Record<string, string> = { ...settings, business_name: val, store_name: val };
                      if (!currentUpi || currentUpi === oldName) {
                        newSettings['upi_name'] = val;
                      }
                      setSettings(newSettings);
                    }} 
                    placeholder="e.g. Soni Jewellers"
                    className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Tagline (Subtitle)</label>
                  <input value={settings['tagline'] || ''} placeholder="e.g. Trust. Purity. Elegance." onChange={e=>setSettings({...settings, tagline: e.target.value})} className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Phone Number</label>
                  <input value={settings['phone'] || ''} onChange={e=>setSettings({...settings, phone: e.target.value})} className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Email Address</label>
                  <input value={settings['email'] || ''} onChange={e=>setSettings({...settings, email: e.target.value})} type="email" className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">GSTIN Number</label>
                  <input value={settings['gstin'] || ''} onChange={e=>setSettings({...settings, gstin: e.target.value})} className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">PAN Number</label>
                  <input value={settings['pan'] || ''} onChange={e=>setSettings({...settings, pan: e.target.value})} className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none" />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Address</label>
                  <textarea value={settings['address'] || ''} onChange={e=>setSettings({...settings, address: e.target.value})} rows={3} className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none resize-none" />
                </div>

                {/* UPI & Payment QR Configuration */}
                <div className="md:col-span-2 mt-4 pt-4 border-t border-gray-800">
                  <h3 className="text-primary font-bold text-sm mb-1 uppercase tracking-widest flex items-center gap-2">
                    <span>UPI & Online Payment QR Settings</span>
                  </h3>
                  <p className="text-xs text-gray-400 mb-4">This UPI ID and QR code will appear directly on customer Tax Invoices & Bills for instant scanning and payment.</p>
                </div>

                <div className="md:col-span-2 bg-black/30 border border-gray-800 rounded-xl p-4 flex flex-col md:flex-row gap-6 items-center">
                  <div className="flex-1 w-full grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-gray-400 uppercase mb-1">UPI ID (VPA)</label>
                      <input 
                        value={settings['upi_id'] || ''} 
                        placeholder="e.g. 9460820878@upi or shop@okhdfcbank" 
                        onChange={e=>setSettings({...settings, upi_id: e.target.value})} 
                        className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none font-mono" 
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-400 uppercase mb-1">UPI Payee / Business Name</label>
                      <input 
                        value={settings['upi_name'] || ''} 
                        placeholder={settings['business_name'] || "e.g. Soni Jewellers"} 
                        onChange={e=>setSettings({...settings, upi_name: e.target.value})} 
                        className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none" 
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Bank Name (Optional)</label>
                      <input 
                        value={settings['bank_name'] || ''} 
                        placeholder="e.g. HDFC Bank / SBI" 
                        onChange={e=>setSettings({...settings, bank_name: e.target.value})} 
                        className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none" 
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Account Number & IFSC (Optional)</label>
                      <div className="grid grid-cols-2 gap-2">
                        <input 
                          value={settings['bank_account_no'] || ''} 
                          placeholder="A/C Number" 
                          onChange={e=>setSettings({...settings, bank_account_no: e.target.value})} 
                          className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none font-mono" 
                        />
                        <input 
                          value={settings['bank_ifsc'] || ''} 
                          placeholder="IFSC Code" 
                          onChange={e=>setSettings({...settings, bank_ifsc: e.target.value})} 
                          className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none font-mono uppercase" 
                        />
                      </div>
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Invoice QR Amount Type</label>
                      <div className="flex flex-col sm:flex-row gap-2 sm:gap-4">
                        <label className="flex items-center gap-2 cursor-pointer text-xs text-gray-300">
                          <input 
                            type="radio" 
                            name="qr_amount_type" 
                            checked={!settings['qr_amount_type'] || settings['qr_amount_type'] === 'exact'} 
                            onChange={()=>setSettings({...settings, qr_amount_type: 'exact'})}
                            className="accent-primary"
                          />
                          <span className="font-semibold text-white">Auto-fill Full Bill Amount</span> (Direct exact bill amount)
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer text-xs text-gray-300">
                          <input 
                            type="radio" 
                            name="qr_amount_type" 
                            checked={settings['qr_amount_type'] === 'custom'} 
                            onChange={()=>setSettings({...settings, qr_amount_type: 'custom'})}
                            className="accent-primary"
                          />
                          <span className="font-semibold text-white">Custom / Open Amount</span> (Customer can type any amount)
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* QR Code Live Preview */}
                  <div className="flex flex-col items-center justify-center p-3 bg-white rounded-lg border border-gray-300 shadow-md min-w-[130px] min-h-[130px]">
                    {settings['upi_id'] ? (
                      <>
                        <img 
                          src={`https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${encodeURIComponent('upi://pay?pa=' + settings['upi_id'] + '&pn=' + encodeURIComponent(settings['upi_name'] || settings['business_name'] || settings['store_name'] || 'Jewellery Store') + '&cu=INR')}`}
                          alt="UPI QR Code Preview"
                          className="w-24 h-24 object-contain"
                        />
                        <div className="text-[10px] font-bold text-black uppercase tracking-wider mt-1">UPI QR Preview</div>
                        <div className="text-[8px] text-gray-600 truncate max-w-[110px]" title={settings['upi_id']}>{settings['upi_id']}</div>
                      </>
                    ) : (
                      <div className="text-center p-2 text-gray-500">
                        <div className="text-[10px] font-bold text-gray-700 uppercase tracking-wider">No UPI ID</div>
                        <div className="text-[8px] text-gray-400 mt-1 max-w-[100px]">Enter UPI ID on left to generate live QR</div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="md:col-span-2 mt-4 pt-4 border-t border-gray-800">
                  <h3 className="text-primary font-bold text-sm mb-4 uppercase tracking-widest">Invoice Print Settings (Other Details)</h3>
                </div>
                
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Print Hallmark</label>
                  <textarea value={settings['print_hallmark'] || ''} placeholder="BIS 916 (Gold)&#10;BIS 925 (Silver)" onChange={e=>setSettings({...settings, print_hallmark: e.target.value})} rows={2} className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none resize-none" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Print Wastage</label>
                  <input value={settings['print_wastage'] || ''} placeholder="0.00%" onChange={e=>setSettings({...settings, print_wastage: e.target.value})} className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Print Making Charges</label>
                  <textarea value={settings['print_making_charges'] || ''} placeholder="Gold ₹ 1,000.00/gm&#10;Silver ₹ 20.00/gm" onChange={e=>setSettings({...settings, print_making_charges: e.target.value})} rows={2} className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none resize-none" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Print Remarks</label>
                  <textarea value={settings['print_remarks'] || ''} placeholder="Subject to realization of cheque." onChange={e=>setSettings({...settings, print_remarks: e.target.value})} rows={2} className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none resize-none" />
                </div>
              </div>
              <div className="pt-4 border-t border-gray-800 mt-4">
                <button type="submit" className="bg-primary hover:bg-primary-dark text-black px-6 py-3 rounded font-bold text-sm transition-colors flex items-center gap-2"><Save size={18} /> Save Settings</button>
              </div>
            </form>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="max-w-2xl space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-textMain mb-2">Account &amp; Security</h2>
              <p className="text-sm text-textMuted">
                Manage your credentials, custom username, password, and account security privileges.
              </p>
            </div>

            {/* Account Credentials Form */}
            <div className="p-6 border border-gray-800 rounded-xl bg-black/20 space-y-6">
              <div className="flex items-center justify-between border-b border-gray-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                    <KeyRound size={20} />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-textMain">Account Credentials &amp; Password</h3>
                    <p className="text-xs text-textMuted">Set your custom username and password for direct sign-in.</p>
                  </div>
                </div>
                {user?.email && (
                  <span className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 inline-flex items-center gap-1">
                    ✓ Google Verified
                  </span>
                )}
              </div>

              <form onSubmit={handleSaveCredentials} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Registered Email (Google Account)</label>
                  <input
                    type="text"
                    disabled
                    value={user?.email || 'Not connected'}
                    className="w-full bg-background/50 border border-gray-800 rounded p-3 text-sm text-gray-400 cursor-not-allowed font-mono"
                  />
                  <p className="text-[11px] text-gray-500 mt-1">
                    Email address is verified via Google Sign-In and cannot be modified.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Full Name</label>
                    <input
                      type="text"
                      value={credFullName}
                      onChange={(e) => setCredFullName(e.target.value)}
                      placeholder="Your Full Name"
                      className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Custom Username</label>
                    <input
                      type="text"
                      value={credUsername}
                      onChange={(e) => setCredUsername(e.target.value)}
                      placeholder="e.g. yash_admin"
                      className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none"
                    />
                    <p className="text-[10px] text-gray-500 mt-1">Can be used to sign in instead of email.</p>
                  </div>
                </div>

                <div className="pt-2 border-t border-gray-800/80">
                  <p className="text-xs font-bold text-primary uppercase tracking-wide mb-3">Update Account Password</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">Current Password</label>
                      <input
                        type="password"
                        value={credCurrentPassword}
                        onChange={(e) => setCredCurrentPassword(e.target.value)}
                        placeholder="Current password"
                        className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">New Password</label>
                      <input
                        type="password"
                        value={credPassword}
                        onChange={(e) => setCredPassword(e.target.value)}
                        placeholder="New password (min 8 chars)"
                        className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">Confirm New Password</label>
                      <input
                        type="password"
                        value={credConfirmPassword}
                        onChange={(e) => setCredConfirmPassword(e.target.value)}
                        placeholder="Re-enter new password"
                        className="w-full bg-background border border-gray-700 rounded p-3 text-sm text-textMain focus:border-primary outline-none"
                      />
                    </div>
                  </div>
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={credLoading}
                    className="bg-primary hover:bg-primary-dark text-black px-6 py-2.5 rounded font-bold text-sm transition-colors flex items-center gap-2 disabled:opacity-50"
                  >
                    <Save size={16} />
                    <span>{credLoading ? 'Saving Credentials...' : 'Save & Update Credentials'}</span>
                  </button>
                </div>
              </form>
            </div>

            {/* RBAC Info */}
            <div className="p-6 border border-gray-800 rounded-xl bg-black/20 text-center">
              <ShieldCheck size={40} className="mx-auto text-primary/40 mb-3" />
              <h3 className="text-sm font-bold text-textMain mb-1">Role-Based Access Control (RBAC)</h3>
              <p className="text-xs text-gray-400 max-w-lg mx-auto">
                Currently logged in as <strong>{user?.role?.name || 'Administrator'}</strong> with full tenant store administration access. All actions are isolated strictly to your store.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'database' && (
          <div className="max-w-3xl">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-textMain">Store Data & Backup</h2>
                <p className="text-sm text-gray-400 mt-1">
                  Private business data management for: <span className="font-semibold text-primary">{storeName}</span>
                </p>
              </div>
              <span className="text-xs px-3 py-1 rounded-full bg-primary/10 border border-primary/30 text-primary font-mono font-medium">
                Store ID: #{user?.store?.id || user?.tenant_id || 1}
              </span>
            </div>

            {/* Multi-Tenant Security & Privacy Banner */}
            <div className="p-4 mb-6 rounded-xl border border-emerald-500/30 bg-emerald-950/20 flex items-start gap-3">
              <ShieldCheck className="text-emerald-400 shrink-0 mt-0.5" size={22} />
              <div className="text-xs text-gray-300 leading-relaxed">
                <span className="font-bold text-emerald-400 block text-sm mb-0.5">100% Isolated Store Data Security</span>
                Your store operates in complete, multi-tenant isolation. All exported backups below contain strictly your store's private records (Invoices, Customers, Inventory, Ledgers, Purchases, and Settings). Other users or stores cannot view or access your data.
              </div>
            </div>

            {/* Backup Cards Grid */}
            <div className="space-y-4">
              {/* Option 1: Master Excel */}
              <div className="p-5 border border-emerald-500/30 rounded-xl bg-black/30 hover:border-emerald-500/50 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1 max-w-lg">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white">Master Excel Spreadsheet (.xlsx)</h3>
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Recommended
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 leading-relaxed">
                    Single curated workbook with separate worksheets for Invoices, Items, Customers, Customer Ledgers, Suppliers, Stock Items, and Expenses. Perfect for accountants and business audits.
                  </p>
                </div>
                <button
                  onClick={handleSingleExcelBackup}
                  className="bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500 hover:text-black px-5 py-2.5 rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2 shrink-0 shadow-lg"
                >
                  <Download size={18} /> Download Excel (.xlsx)
                </button>
              </div>

              {/* Option 2: Excel ZIP */}
              <div className="p-5 border border-gray-800 rounded-xl bg-black/20 hover:border-gray-700 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1 max-w-lg">
                  <h3 className="text-base font-bold text-white">All Tables Archive (Excel ZIP)</h3>
                  <p className="text-xs text-gray-400 leading-relaxed">
                    Compressed ZIP folder containing individual Excel (.xlsx) files for every database table of your store.
                  </p>
                </div>
                <button
                  onClick={handleExcelBackup}
                  className="bg-gray-800 text-gray-200 border border-gray-700 hover:bg-gray-700 hover:text-white px-5 py-2.5 rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2 shrink-0"
                >
                  <Download size={18} /> Download ZIP Archive
                </button>
              </div>

              {/* Option 3: SQL Script */}
              <div className="p-5 border border-gray-800 rounded-xl bg-black/20 hover:border-gray-700 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1 max-w-lg">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white">Store Database Dump (.sql)</h3>
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-primary/20 text-primary border border-primary/30">
                      Technical
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 leading-relaxed">
                    Full structured SQL script containing INSERT statements for your store's records. Useful for technical developer archival.
                  </p>
                </div>
                <button
                  onClick={handleBackup}
                  className="bg-primary/20 text-primary border border-primary/30 hover:bg-primary hover:text-black px-5 py-2.5 rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2 shrink-0"
                >
                  <Download size={18} /> Download SQL (.sql)
                </button>
              </div>
            </div>

            {/* Cloud Safety & Multi-Tenant Assurance Card */}
            <div className="p-6 border border-gray-800 rounded-xl bg-surface/60 mt-6 space-y-3">
              <div className="flex items-center gap-2">
                <Database className="text-primary" size={20} />
                <h3 className="text-base font-bold text-white">Data Restoration & Multi-Tenant Cloud Safety</h3>
              </div>
              <p className="text-xs text-gray-400 leading-relaxed">
                Because this system operates on a centralized multi-tenant cloud database, manual database file replacements are strictly disabled. This guarantees that your business records are always protected from accidental overwrites.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs">
                <div className="p-3 bg-black/30 border border-gray-800/80 rounded-lg">
                  <span className="font-semibold text-gray-200 block mb-1">Point-in-Time Backup</span>
                  Your downloaded Master Excel workbook contains complete customer ledgers, stock weights, and invoice history that you can view and print anytime offline.
                </div>
                <div className="p-3 bg-black/30 border border-gray-800/80 rounded-lg">
                  <span className="font-semibold text-gray-200 block mb-1">Zero Overwrite Guarantee</span>
                  Every record is permanently scoped to Store ID #{user?.store?.id || user?.tenant_id || 1}, ensuring total privacy and immunity from actions of other stores.
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
