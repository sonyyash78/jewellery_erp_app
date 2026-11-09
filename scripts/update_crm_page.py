import os

def update_crm(file_path):
    if not os.path.exists(file_path):
        print(f"Skipping {file_path} - not found")
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add RefreshCcw & useCompanyStore
    if 'RefreshCcw' not in content:
        content = content.replace("Search, X", "Search, X, RefreshCcw")
    if 'useCompanyStore' not in content:
        content = content.replace("import toast from 'react-hot-toast';", "import toast from 'react-hot-toast';\nimport { useCompanyStore } from '../../store/companyStore';")

    # Add currentCompanyId & loading state
    target_start = "export default function CRM() {"
    if "const { currentCompanyId } = useCompanyStore();" not in content:
        replacement_start = "export default function CRM() {\n  const { currentCompanyId } = useCompanyStore();\n  const [loading, setLoading] = useState(false);"
        content = content.replace(target_start, replacement_start, 1)

    # Replace fetchData & useEffect
    old_fetch_snippet = """  const fetchData = async () => {
    try {
      const [custRes, suppRes] = await Promise.all([
        axiosClient.get('/customers/', { params: { search } }),
        axiosClient.get('/sellers/', { params: { search } })
      ]);
      setCustomers(custRes.data.items);
      setSuppliers(suppRes.data.items);
      setMetrics({
        totalCustomers: custRes.data.total,
        totalSuppliers: suppRes.data.total,
        outstanding: custRes.data.total_outstanding - suppRes.data.total_outstanding // Net outstanding (we receive - we pay)
      });
    } catch (e) {
      toast.error('Failed to load CRM data');
    }
  };

  useEffect(() => {
    fetchData();
  }, [search]);"""

    new_fetch_snippet = """  const fetchData = async () => {
    setLoading(true);
    try {
      const [custRes, suppRes] = await Promise.all([
        axiosClient.get('/customers/', { params: { search: search || undefined } }),
        axiosClient.get('/sellers/', { params: { search: search || undefined } })
      ]);
      const custList = Array.isArray(custRes.data) ? custRes.data : (custRes.data?.items || []);
      const suppList = Array.isArray(suppRes.data) ? suppRes.data : (suppRes.data?.items || []);
      setCustomers(custList);
      setSuppliers(suppList);
      const totalCust = custRes.data?.total ?? custList.length;
      const totalSupp = suppRes.data?.total ?? suppList.length;
      const custOut = Number(custRes.data?.total_outstanding) || 0;
      const suppOut = Number(suppRes.data?.total_outstanding) || 0;
      setMetrics({
        totalCustomers: totalCust,
        totalSuppliers: totalSupp,
        outstanding: custOut - suppOut
      });
    } catch (e) {
      console.error('Failed to load CRM data', e);
      toast.error('Failed to load CRM data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [search, currentCompanyId]);"""

    content = content.replace(old_fetch_snippet, new_fetch_snippet)

    # Add Refresh button next to search box
    old_search_box = """          <div className="w-full sm:w-64 p-3 relative border-t sm:border-t-0 border-gray-800">
            <Search className="absolute left-6 top-5 text-gray-500" size={18} />
            <input 
              value={search} onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-background border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-sm text-textMain focus:border-primary outline-none" 
              placeholder={tab === 'customers' ? "Search customers..." : "Search suppliers..."} 
            />
          </div>"""

    new_search_box = """          <div className="w-full sm:w-80 p-3 flex items-center gap-2 border-t sm:border-t-0 border-gray-800">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 text-gray-500" size={18} />
              <input 
                value={search} onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-background border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-sm text-textMain focus:border-primary outline-none" 
                placeholder={tab === 'customers' ? "Search customers..." : "Search suppliers..."} 
              />
            </div>
            <button
              onClick={fetchData}
              disabled={loading}
              title="Refresh CRM Data"
              className="p-2.5 rounded-lg border border-gray-700 bg-background hover:bg-gray-800 text-gray-300 hover:text-primary transition-all disabled:opacity-50"
            >
              <RefreshCcw size={16} className={loading ? 'animate-spin text-primary' : ''} />
            </button>
          </div>"""

    content = content.replace(old_search_box, new_search_box)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {file_path} successfully")

update_crm(r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\crm\index.tsx')
update_crm(r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\pages\crm\index.tsx')
