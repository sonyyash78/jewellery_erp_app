import os

p = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\settings\index.tsx"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Add import
if "import { useCompanyStore } from '../../store/companyStore';" not in c:
    c = c.replace(
        "import { useAuthStore } from '../../store/authStore';",
        "import { useAuthStore } from '../../store/authStore';\nimport { useCompanyStore } from '../../store/companyStore';"
    )

# 2. Add state inside Settings component
state_target = "  const [settings, setSettings] = useState<Record<string, string>>({});"
state_code = """  const { companies, currentCompanyId, fetchCompanies } = useCompanyStore();
  const [selectedCompanyId, setSelectedCompanyId] = useState<number>(currentCompanyId || 1);
  const [companyForm, setCompanyForm] = useState({
    name: '',
    address: '',
    city: '',
    state: 'Rajasthan',
    state_code: '08',
    gstin: '',
    pan: '',
    phone: '',
    email: '',
    jurisdiction_city: 'JODHPUR',
    declaration: ''
  });
  const [savingCompany, setSavingCompany] = useState(false);

  useEffect(() => {
    fetchCompanies();
  }, []);

  useEffect(() => {
    const co = companies.find(c => c.id === selectedCompanyId) || companies.find(c => c.id === 1);
    if (co) {
      setCompanyForm({
        name: co.name || '',
        address: co.address || '',
        city: co.city || '',
        state: co.state || 'Rajasthan',
        state_code: co.state_code || '08',
        gstin: co.gstin || '',
        pan: co.pan || '',
        phone: co.phone || '',
        email: co.email || '',
        jurisdiction_city: co.jurisdiction_city || (co.gst_enabled ? 'JODHPUR' : 'TAKHATGARH'),
        declaration: co.declaration || ''
      });
    }
  }, [selectedCompanyId, companies]);

  const handleSaveCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingCompany(true);
    try {
      await axiosClient.put(`/companies/${selectedCompanyId}`, companyForm);
      toast.success(`${companyForm.name} details saved successfully!`);
      await fetchCompanies();
      await fetchSettings();
      window.dispatchEvent(new Event('settings-updated'));
    } catch (err: any) {
      toast.error(getErrorMessage(err, 'Failed to update company details'));
    } finally {
      setSavingCompany(false);
    }
  };

  const [settings, setSettings] = useState<Record<string, string>>({});"""

if "const [companyForm, setCompanyForm]" not in c:
    c = c.replace(state_target, state_code, 1)

# 3. Add UI card in activeTab === 'profile'
profile_card_target = '<h2 className="text-2xl font-bold text-textMain mb-6">Business Profile</h2>'
profile_card_code = """<h2 className="text-2xl font-bold text-textMain mb-6">Business Profile & Operating Companies</h2>

            {/* Multi-Company Seller Details Card */}
            <div className="mb-8 p-5 border border-gray-800 rounded-2xl bg-[#14141B] shadow-xl">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-5 pb-4 border-b border-gray-800">
                <div>
                  <h3 className="text-base font-extrabold text-white uppercase tracking-wider flex items-center gap-2">
                    <Building2 size={20} className="text-primary" />
                    Operating Company & Seller Address (कंपनी नाम व पता)
                  </h3>
                  <p className="text-xs text-gray-400 mt-1">
                    Select company below to edit its name, address, GSTIN, and contact details shown on invoices.
                  </p>
                </div>
                <div className="flex gap-2 shrink-0">
                  {companies.map(c => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setSelectedCompanyId(c.id)}
                      className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                        selectedCompanyId === c.id
                          ? c.gst_enabled
                            ? 'bg-cyan-500 text-black shadow-lg shadow-cyan-500/20'
                            : 'bg-primary text-black shadow-lg shadow-primary/20'
                          : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
                      }`}
                    >
                      {c.gst_enabled ? '💎 ' + c.name + ' (GST)' : '🏛️ ' + c.name + ' (Normal)'}
                    </button>
                  ))}
                </div>
              </div>

              <form onSubmit={handleSaveCompany} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Seller / Company Name</label>
                    <input 
                      value={companyForm.name} 
                      onChange={e => setCompanyForm({ ...companyForm, name: e.target.value })} 
                      placeholder="e.g. PRIDE GOLD or SAIDEEP JEWELLERS"
                      className="w-full bg-background border border-gray-700 rounded p-2.5 text-sm text-white focus:border-primary outline-none font-semibold" 
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Phone Number(s)</label>
                    <input 
                      value={companyForm.phone} 
                      onChange={e => setCompanyForm({ ...companyForm, phone: e.target.value })} 
                      placeholder="e.g. 0291-2640999, +91-9929562800"
                      className="w-full bg-background border border-gray-700 rounded p-2.5 text-sm text-white focus:border-primary outline-none" 
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">GSTIN Number</label>
                    <input 
                      value={companyForm.gstin} 
                      onChange={e => setCompanyForm({ ...companyForm, gstin: e.target.value.toUpperCase() })} 
                      placeholder="e.g. 08AEZPK5007N1ZS"
                      className="w-full bg-background border border-gray-700 rounded p-2.5 text-sm text-white focus:border-primary outline-none font-mono" 
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Company PAN</label>
                    <input 
                      value={companyForm.pan} 
                      onChange={e => setCompanyForm({ ...companyForm, pan: e.target.value.toUpperCase() })} 
                      placeholder="e.g. AEZPK5007N"
                      className="w-full bg-background border border-gray-700 rounded p-2.5 text-sm text-white focus:border-primary outline-none font-mono" 
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Email Address</label>
                    <input 
                      value={companyForm.email} 
                      onChange={e => setCompanyForm({ ...companyForm, email: e.target.value })} 
                      type="email" 
                      placeholder="e.g. info.pridegoldjdr@gmail.com"
                      className="w-full bg-background border border-gray-700 rounded p-2.5 text-sm text-white focus:border-primary outline-none" 
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Jurisdiction City</label>
                    <input 
                      value={companyForm.jurisdiction_city} 
                      onChange={e => setCompanyForm({ ...companyForm, jurisdiction_city: e.target.value })} 
                      placeholder="e.g. JODHPUR"
                      className="w-full bg-background border border-gray-700 rounded p-2.5 text-sm text-white focus:border-primary outline-none" 
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Seller Address (Full)</label>
                    <textarea 
                      value={companyForm.address} 
                      onChange={e => setCompanyForm({ ...companyForm, address: e.target.value })} 
                      rows={3} 
                      placeholder="e.g. 1st Floor, Near Koira Ji ka Bera, Ghodo ka Chowk, Sojati Gate, Jodhpur (Raj.)- 342001"
                      className="w-full bg-background border border-gray-700 rounded p-2.5 text-sm text-white focus:border-primary outline-none resize-none" 
                    />
                  </div>
                  <div className="md:col-span-2 flex justify-end">
                    <button
                      type="submit"
                      disabled={savingCompany}
                      className="px-6 py-2.5 bg-primary text-black font-bold text-xs rounded-xl hover:bg-primary-dark transition-all shadow-md flex items-center gap-2 cursor-pointer disabled:opacity-50"
                    >
                      <Save size={16} /> {savingCompany ? 'Saving...' : 'Save Company Details'}
                    </button>
                  </div>
                </div>
              </form>
            </div>"""

if "Operating Company & Seller Address (कंपनी नाम व पता)" not in c:
    c = c.replace(profile_card_target, profile_card_code, 1)

with open(p, "w", encoding="utf-8") as f:
    f.write(c)

print("Updated settings/index.tsx with full Company Editor")
