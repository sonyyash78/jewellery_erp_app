from pathlib import Path

history_file = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\invoices\InvoiceHistory.tsx")
code = history_file.read_text(encoding="utf-8")

# 1. Add RotateCw to imports
old_imp = """  ChevronLeft,

  ChevronRight

} from 'lucide-react';"""

new_imp = """  ChevronLeft,
  ChevronRight,
  RotateCw
} from 'lucide-react';"""

code = code.replace(old_imp, new_imp)

# 2. Add syncingVault state and handleRefreshAllVaultPdfs
old_state = """  const [showPreviewModal, setShowPreviewModal] = useState(false);

  const itemsPerPage = 10;"""

new_state = """  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [syncingVault, setSyncingVault] = useState(false);

  const handleRefreshAllVaultPdfs = async () => {
    try {
      setSyncingVault(true);
      toast.loading('Refreshing all PDFs into GST & Without_GST folders...', { id: 'vault-sync' });
      await axiosClient.post('/backup/archive-pdfs', { force_refresh: true });
      const electronAPI = (window as any).electronAPI;
      if (electronAPI?.backupToUsb) {
        await electronAPI.backupToUsb();
      }
      toast.success('All bills & statements auto-saved to PC & Pendrive!', { id: 'vault-sync' });
      fetchInvoices();
    } catch (err: any) {
      console.error('Vault sync error:', err);
      toast.error('Failed to sync vault PDFs', { id: 'vault-sync' });
    } finally {
      setSyncingVault(false);
    }
  };

  const itemsPerPage = 10;"""

code = code.replace(old_state, new_state)

# 3. Add button in header
old_hdr = """      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-primary">Invoice History</h1>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold font-mono border ${currentCompanyId === 2 ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'}`}>
              {currentCompanyId === 2 ? '💎 SAIDEEP JEWELLERS (GST)' : '🏛️ SAIDEEP JEWELLERS (Normal)'}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-textMuted mt-0.5 sm:mt-1">
            Viewing strictly isolated {currentCompanyId === 2 ? 'GST Tax Invoices for Saideep Jewellers' : 'retail non-GST invoices for Saideep Jewellers'}
          </p>
        </div>
      </div>"""

new_hdr = """      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-primary">Invoice History</h1>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold font-mono border ${currentCompanyId === 2 ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'}`}>
              {currentCompanyId === 2 ? '💎 SAIDEEP JEWELLERS (GST)' : '🏛️ SAIDEEP JEWELLERS (Normal)'}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-textMuted mt-0.5 sm:mt-1">
            Viewing strictly isolated {currentCompanyId === 2 ? 'GST Tax Invoices for Saideep Jewellers' : 'retail non-GST invoices for Saideep Jewellers'}
          </p>
        </div>
        <button
          onClick={handleRefreshAllVaultPdfs}
          disabled={syncingVault}
          className="flex items-center gap-2 bg-primary/20 hover:bg-primary/30 text-primary border border-primary/40 px-3 py-2 rounded-lg text-xs font-bold transition-all disabled:opacity-50 cursor-pointer shadow-[0_0_10px_rgba(212,175,55,0.2)]"
          title="Refresh and auto-save all bills across database into GST & Without_GST folders"
        >
          <RotateCw size={14} className={syncingVault ? 'animate-spin' : ''} />
          <span>{syncingVault ? 'Auto-Saving Vault...' : 'Refresh & Auto-Save PDFs'}</span>
        </button>
      </div>"""

code = code.replace(old_hdr, new_hdr)

history_file.write_text(code, encoding="utf-8")
print("InvoiceHistory.tsx updated successfully!")
