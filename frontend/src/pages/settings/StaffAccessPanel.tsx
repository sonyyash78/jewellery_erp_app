import { useState, useEffect } from 'react';
import { axiosClient } from '../../api/axiosClient';
import { getErrorMessage } from '../../utils/errorUtils';
import {
  Users,
  UserPlus,
  Shield,
  Edit2,
  Trash2,
  Lock,
  Unlock,
  Check,
  X,
  KeyRound,
  Eye,
  EyeOff,
  ShieldCheck,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface StaffMember {
  id: number;
  username: string;
  full_name: string;
  is_active: boolean;
  role_name: string;
  allowed_modules: string[];
  created_at?: string;
}

const MODULE_DEFINITIONS = [
  { key: 'billing', label: 'POS Billing', desc: 'Create new sales bills & checkout' },
  { key: 'invoices', label: 'Invoices History', desc: 'View & print past customer bills' },
  { key: 'exchange', label: 'Old Gold Exchange', desc: 'Old gold & silver exchange counter' },
  { key: 'customers', label: 'Customers & Suppliers', desc: 'View CRM profiles, ledgers & settlements' },
  { key: 'inventory', label: 'Inventory & Stock', desc: 'Manage jewellery items & QR tags' },
  { key: 'purchases', label: 'Purchases', desc: 'Record supplier purchase bills' },
  { key: 'dashboard', label: 'Dashboard KPIs', desc: 'Store sales overview & daily summary' },
  { key: 'reports', label: 'Reports & Profit', desc: 'Sales, metal & profit margin analytics' },
  { key: 'settings', label: 'Settings & Backup', desc: 'Store configuration & database backups' },
];

const ROLE_PRESETS: Record<string, { label: string; badgeColor: string; modules: string[]; summary: string }> = {
  'Sales Staff': {
    label: 'Sales / Billing Staff',
    badgeColor: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    modules: ['billing', 'invoices', 'exchange', 'customers', 'inventory'],
    summary: 'Ideal for counter sales staff. Can create bills, exchanges, and view stock/customers. Cannot see profit reports or settings.',
  },
  'Store Manager': {
    label: 'Store Manager',
    badgeColor: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    modules: ['dashboard', 'customers', 'inventory', 'billing', 'invoices', 'exchange', 'purchases', 'reports'],
    summary: 'Full operational access including purchases, dashboard, and reports, without store backup/security settings.',
  },
  'Inventory Staff': {
    label: 'Inventory / Stock Staff',
    badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    modules: ['inventory', 'purchases'],
    summary: 'Focused on adding stock items, printing QR tags, and recording supplier purchase entries.',
  },
};

export default function StaffAccessPanel() {
  const [staffList, setStaffList] = useState<StaffMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState<StaffMember | null>(null);
  const [saving, setSaving] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Form states
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [roleName, setRoleName] = useState<string>('Sales Staff');
  const [allowedModules, setAllowedModules] = useState<string[]>(ROLE_PRESETS['Sales Staff'].modules);

  const fetchStaff = async () => {
    setLoading(true);
    try {
      const res = await axiosClient.get('/staff/');
      setStaffList(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast.error(getErrorMessage(err, 'Failed to load staff members'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStaff();
  }, []);

  const openCreateModal = () => {
    setEditingStaff(null);
    setFullName('');
    setUsername('');
    setPassword('');
    setRoleName('Sales Staff');
    setAllowedModules([...ROLE_PRESETS['Sales Staff'].modules]);
    setShowPassword(false);
    setModalOpen(true);
  };

  const openEditModal = (staff: StaffMember) => {
    setEditingStaff(staff);
    setFullName(staff.full_name || '');
    setUsername(staff.username || '');
    setPassword('');
    const matchedRole = ROLE_PRESETS[staff.role_name] ? staff.role_name : 'Sales Staff';
    setRoleName(matchedRole);
    setAllowedModules(
      Array.isArray(staff.allowed_modules) && staff.allowed_modules.length > 0
        ? [...staff.allowed_modules]
        : [...ROLE_PRESETS[matchedRole].modules]
    );
    setShowPassword(false);
    setModalOpen(true);
  };

  const handleSelectRolePreset = (role: string) => {
    setRoleName(role);
    if (ROLE_PRESETS[role]) {
      setAllowedModules([...ROLE_PRESETS[role].modules]);
    }
  };

  const toggleModule = (modKey: string) => {
    setAllowedModules(prev =>
      prev.includes(modKey) ? prev.filter(m => m !== modKey) : [...prev, modKey]
    );
  };

  const handleSaveStaff = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) {
      toast.error('Please enter staff member full name');
      return;
    }
    if (username.trim().length < 3) {
      toast.error('Username must be at least 3 characters');
      return;
    }
    if (!editingStaff && password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }
    if (editingStaff && password && password.length < 6) {
      toast.error('New password must be at least 6 characters');
      return;
    }
    if (allowedModules.length === 0) {
      toast.error('Please select at least one module for this staff member');
      return;
    }

    setSaving(true);
    try {
      if (editingStaff) {
        await axiosClient.put(`/staff/${editingStaff.id}`, {
          full_name: fullName.trim(),
          username: username.trim(),
          password: password || undefined,
          role_name: roleName,
          allowed_modules: allowedModules,
        });
        toast.success('Staff member access updated!');
      } else {
        await axiosClient.post('/staff/', {
          full_name: fullName.trim(),
          username: username.trim(),
          password,
          role_name: roleName,
          allowed_modules: allowedModules,
        });
        toast.success('Staff account created successfully!');
      }
      setModalOpen(false);
      await fetchStaff();
    } catch (err) {
      toast.error(getErrorMessage(err, 'Failed to save staff account'));
    } finally {
      setSaving(false);
    }
  };

  const handleToggleActive = async (staff: StaffMember) => {
    try {
      const nextStatus = !staff.is_active;
      await axiosClient.put(`/staff/${staff.id}`, {
        is_active: nextStatus,
      });
      toast.success(
        nextStatus
          ? `${staff.full_name || staff.username} login activated`
          : `${staff.full_name || staff.username} login blocked`
      );
      await fetchStaff();
    } catch (err) {
      toast.error(getErrorMessage(err, 'Failed to update staff status'));
    }
  };

  const handleDeleteStaff = async (staff: StaffMember) => {
    if (!window.confirm(`Are you sure you want to remove staff account "${staff.full_name || staff.username}"?`)) {
      return;
    }
    try {
      await axiosClient.delete(`/staff/${staff.id}`);
      toast.success('Staff account removed');
      await fetchStaff();
    } catch (err) {
      toast.error(getErrorMessage(err, 'Failed to remove staff account'));
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Users className="text-primary" size={22} /> Staff Accounts &amp; Access Control
          </h3>
          <p className="text-xs text-textMuted mt-1">
            Create dedicated logins for your store staff and control which modules (Billing, Inventory, Reports, etc.) they can access.
          </p>
        </div>
        <button
          type="button"
          onClick={openCreateModal}
          className="bg-primary text-black font-bold px-4 py-2.5 rounded-lg hover:bg-primary/90 transition-colors flex items-center justify-center gap-2 text-xs sm:text-sm shrink-0 shadow-[0_0_15px_rgba(212,175,55,0.25)]"
        >
          <UserPlus size={17} /> Add Staff Member
        </button>
      </div>

      {/* Role Presets Guide */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {Object.entries(ROLE_PRESETS).map(([roleKey, preset]) => (
          <div
            key={roleKey}
            className="bg-background/60 border border-gray-800 rounded-xl p-3.5 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <span className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${preset.badgeColor}`}>
                  {preset.label}
                </span>
                <span className="text-[11px] text-gray-500 font-mono">{preset.modules.length} modules</span>
              </div>
              <p className="text-xs text-gray-400 leading-relaxed">{preset.summary}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Staff Accounts Table / List */}
      <div className="bg-background border border-gray-800 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-800 bg-gray-900/50 flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-gray-300 flex items-center gap-2">
            <ShieldCheck size={15} className="text-primary" /> Store Staff Members ({staffList.length})
          </span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">Loading staff accounts...</div>
        ) : staffList.length === 0 ? (
          <div className="p-10 text-center flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
              <Users size={22} />
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-white">No Staff Accounts Created Yet</h4>
              <p className="text-xs text-gray-400 max-w-md">
                Click &ldquo;Add Staff Member&rdquo; above to create a username &amp; password for your salesperson, cashier, or manager with restricted access.
              </p>
            </div>
            <button
              type="button"
              onClick={openCreateModal}
              className="mt-1 bg-primary/20 text-primary border border-primary/40 hover:bg-primary hover:text-black font-bold text-xs px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5"
            >
              <UserPlus size={15} /> Create First Staff Account
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-800">
            {staffList.map(staff => {
              const rolePreset = ROLE_PRESETS[staff.role_name];
              const badgeClass = rolePreset?.badgeColor || 'bg-gray-800 text-gray-300 border-gray-700';
              const mods = Array.isArray(staff.allowed_modules) ? staff.allowed_modules : [];

              return (
                <div
                  key={staff.id}
                  className="p-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4 hover:bg-gray-900/30 transition-colors"
                >
                  <div className="space-y-2 min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm sm:text-base font-bold text-white truncate">
                        {staff.full_name || staff.username}
                      </span>
                      <span className="text-xs font-mono text-primary bg-primary/10 border border-primary/20 px-2 py-0.5 rounded">
                        @{staff.username}
                      </span>
                      <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${badgeClass}`}>
                        {staff.role_name}
                      </span>
                      <span
                        className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                          staff.is_active
                            ? 'bg-green-500/15 text-green-400 border border-green-500/30'
                            : 'bg-red-500/15 text-red-400 border border-red-500/30'
                        }`}
                      >
                        {staff.is_active ? 'Active' : 'Blocked'}
                      </span>
                    </div>

                    {/* Allowed Modules Pills */}
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] text-gray-500 uppercase tracking-wider mr-1">Access:</span>
                      {MODULE_DEFINITIONS.filter(m => mods.includes(m.key)).map(m => (
                        <span
                          key={m.key}
                          className="text-[11px] bg-gray-800/90 text-gray-300 border border-gray-700 px-2 py-0.5 rounded"
                        >
                          {m.label}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-wrap items-center gap-2 shrink-0">
                    <button
                      type="button"
                      onClick={() => openEditModal(staff)}
                      className="bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
                    >
                      <Edit2 size={13} /> Edit Access / Password
                    </button>
                    <button
                      type="button"
                      onClick={() => handleToggleActive(staff)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold border flex items-center gap-1.5 transition-colors ${
                        staff.is_active
                          ? 'bg-amber-500/10 text-amber-300 border-amber-500/30 hover:bg-amber-500/20'
                          : 'bg-green-500/10 text-green-300 border-green-500/30 hover:bg-green-500/20'
                      }`}
                    >
                      {staff.is_active ? (
                        <>
                          <Lock size={13} /> Block Login
                        </>
                      ) : (
                        <>
                          <Unlock size={13} /> Unblock
                        </>
                      )}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDeleteStaff(staff)}
                      className="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 p-1.5 rounded-lg transition-colors"
                      title="Delete Staff Account"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create / Edit Staff Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-surface border border-gray-800 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden my-8">
            <div className="px-5 py-4 border-b border-gray-800 flex items-center justify-between bg-black/30">
              <div className="flex items-center gap-2">
                <Shield className="text-primary" size={20} />
                <h3 className="text-base sm:text-lg font-bold text-white">
                  {editingStaff ? `Edit Staff: ${editingStaff.full_name || editingStaff.username}` : 'Add New Staff Member'}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-gray-800"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSaveStaff} className="p-5 space-y-5 max-h-[80vh] overflow-y-auto custom-scrollbar">
              {/* Basic Credentials */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-textMuted uppercase mb-1.5">
                    Staff Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={e => setFullName(e.target.value)}
                    placeholder="e.g. Rahul Sharma"
                    className="w-full bg-background border border-gray-700 rounded-lg px-3.5 py-2.5 text-sm text-white focus:border-primary outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-textMuted uppercase mb-1.5">
                    Login Username *
                  </label>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                    placeholder="e.g. rahul_staff"
                    className="w-full bg-background border border-gray-700 rounded-lg px-3.5 py-2.5 text-sm text-white font-mono focus:border-primary outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-textMuted uppercase mb-1.5 flex items-center gap-1.5">
                  <KeyRound size={13} className="text-primary" />
                  {editingStaff ? 'New Password (leave blank to keep current)' : 'Login Password *'}
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required={!editingStaff}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder={editingStaff ? 'Enter new password to reset...' : 'Minimum 6 characters'}
                    className="w-full bg-background border border-gray-700 rounded-lg px-3.5 py-2.5 pr-10 text-sm text-white focus:border-primary outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {/* Role Preset Selection */}
              <div>
                <label className="block text-xs font-bold text-textMuted uppercase mb-2">
                  Select Staff Role Preset
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                  {Object.entries(ROLE_PRESETS).map(([rKey, preset]) => {
                    const active = roleName === rKey;
                    return (
                      <button
                        key={rKey}
                        type="button"
                        onClick={() => handleSelectRolePreset(rKey)}
                        className={`p-3 rounded-xl border text-left transition-all ${
                          active
                            ? 'bg-primary/15 border-primary text-white shadow-[0_0_12px_rgba(212,175,55,0.15)]'
                            : 'bg-background border-gray-800 text-gray-400 hover:border-gray-700'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-bold text-white">{rKey}</span>
                          {active && <Check size={14} className="text-primary" />}
                        </div>
                        <p className="text-[11px] text-gray-400 line-clamp-2">{preset.summary}</p>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Granular Module Checkboxes */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-bold text-textMuted uppercase">
                    Module Access Permissions ({allowedModules.length} of {MODULE_DEFINITIONS.length} enabled)
                  </label>
                  <div className="flex items-center gap-3 text-xs">
                    <button
                      type="button"
                      onClick={() => setAllowedModules(MODULE_DEFINITIONS.map(m => m.key))}
                      className="text-primary hover:underline"
                    >
                      Select All
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        setAllowedModules([...(ROLE_PRESETS[roleName]?.modules || ['billing', 'invoices'])])
                      }
                      className="text-gray-400 hover:text-white"
                    >
                      Reset to Default
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {MODULE_DEFINITIONS.map(mod => {
                    const checked = allowedModules.includes(mod.key);
                    return (
                      <label
                        key={mod.key}
                        onClick={() => toggleModule(mod.key)}
                        className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-colors select-none ${
                          checked
                            ? 'bg-primary/10 border-primary/40 text-white'
                            : 'bg-background/60 border-gray-800 text-gray-400 hover:border-gray-700'
                        }`}
                      >
                        <div
                          className={`mt-0.5 w-4 h-4 rounded flex items-center justify-center border shrink-0 ${
                            checked ? 'bg-primary border-primary text-black' : 'border-gray-600 bg-transparent'
                          }`}
                        >
                          {checked && <Check size={12} strokeWidth={3} />}
                        </div>
                        <div className="min-w-0">
                          <div className="text-xs font-bold text-white">{mod.label}</div>
                          <div className="text-[11px] text-gray-400">{mod.desc}</div>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Footer Buttons */}
              <div className="flex items-center justify-end gap-3 pt-3 border-t border-gray-800">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="bg-primary text-black font-bold px-5 py-2.5 rounded-lg hover:bg-primary/90 transition-colors text-xs sm:text-sm disabled:opacity-50"
                >
                  {saving ? 'Saving...' : editingStaff ? 'Save Changes' : 'Create Staff Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
