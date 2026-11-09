path = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\TopBar.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace handleSelectSaideep
old_func = """  const handleSelectSaideep = () => {
    const saideep = customers.find(c => 
      c.first_name?.toLowerCase().includes('saideep') || 
      c.phone_number === '9460820878' ||
      c.gst_number === '08BNUPK1610E1Z3'
    );
    if (saideep) {
      setSelectedCustomerId(saideep.id);
    }
  };"""

text = text.replace(old_func, "")

# Remove button
old_button = """        {/* Quick select Saideep Jewellers as Buyer for Pride Gold GST invoices */}
        {isGst && (
          <button
            type="button"
            onClick={handleSelectSaideep}
            title="Auto-select Saideep Jewellers (Takhatgarh) as Buyer"
            className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-cyan-950/40 border border-cyan-600/50 text-cyan-300 hover:bg-cyan-900/50 text-xs font-semibold whitespace-nowrap transition-all shadow-sm"
          >
            <Sparkles size={13} className="text-cyan-400" /> Bill to Saideep Jewellers
          </button>
        )}"""

text = text.replace(old_button, "")

text = text.replace("'PG/S/AUTO'", "'SJ/S/AUTO'")
text = text.replace("{isGst ? 'Pride Gold GST' : 'Billing Studio'}", "{isGst ? 'Saideep GST' : 'Billing Studio'}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated TopBar.tsx successfully!')
