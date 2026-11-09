import os
import re

p_hist = r"c:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\invoices\InvoiceHistory.tsx"
with open(p_hist, "r", encoding="utf-8") as f:
    c = f.read()

is_crlf = "\r\n" in c
c = c.replace("\r\n", "\n")

# Import
if "import { useCompanyStore } from '../../store/companyStore';" not in c:
    c = c.replace(
        "import InvoicePreviewModal from '../../components/invoices/InvoicePreviewModal';",
        "import InvoicePreviewModal from '../../components/invoices/InvoicePreviewModal';\nimport { useCompanyStore } from '../../store/companyStore';"
    )

# Function body
pattern_fn = r'export default function InvoiceHistory\(\)\s*\{\s*const \[tab, setTab\] = useState<(\'sales\' \| \'purchases\' \| \'exchanges\')>\(\'sales\'\);'
repl_fn = """export default function InvoiceHistory() {
  const { currentCompanyId, currentCompany } = useCompanyStore();
  const [tab, setTab] = useState<'sales' | 'purchases' | 'exchanges'>('sales');"""

c, count_fn = re.subn(pattern_fn, repl_fn, c, count=1)
print("Replaced fn:", count_fn)

# Effect
pattern_effect = r'useEffect\(\(\) => \{\s*fetchInvoices\(\);\s*\}, \[searchTerm, statusFilter, currentPage, tab\]\);'
repl_effect = """// Reset pagination on company switch
  useEffect(() => {
    setCurrentPage(1);
  }, [currentCompanyId]);

  useEffect(() => {
    fetchInvoices();
  }, [searchTerm, statusFilter, currentPage, tab, currentCompanyId]);"""

c, count_effect = re.subn(pattern_effect, repl_effect, c, count=1)
print("Replaced effect:", count_effect)

# Params
pattern_params = r'if \(searchTerm\) params\.append\(\'search\', searchTerm\);'
repl_params = "params.append('company_id', String(currentCompanyId || 1));\n      if (searchTerm) params.append('search', searchTerm);"
c, count_params = re.subn(pattern_params, repl_params, c, count=1)
print("Replaced params:", count_params)

# Header badge
pattern_header = r'{\s*/\*\s*Header\s*\*/\s*}\s*<div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">\s*<div>\s*<h1 className="text-xl sm:text-2xl font-bold text-primary">Invoice History</h1>\s*<p className="text-xs sm:text-sm text-textMuted mt-0\.5 sm:mt-1">View and manage all generated invoices across categories</p>\s*</div>\s*</div>'

repl_header = """{/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-primary">Invoice History</h1>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold font-mono border ${currentCompanyId === 2 ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'}`}>
              {currentCompanyId === 2 ? '💎 Pride Gold (GST)' : '🏛️ Saideep Jewellers (Normal)'}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-textMuted mt-0.5 sm:mt-1">
            Viewing strictly isolated {currentCompanyId === 2 ? 'GST Tax Invoices for Pride Gold' : 'invoices for Saideep Jewellers'}
          </p>
        </div>
      </div>"""

c, count_header = re.subn(pattern_header, repl_header, c, count=1)
print("Replaced header:", count_header)

final_c = c.replace("\n", "\r\n") if is_crlf else c
with open(p_hist, "w", encoding="utf-8") as f:
    f.write(final_c)

print("Saved InvoiceHistory.tsx successfully")
