import os

modal_path = r'c:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\CheckoutModal.tsx'
with open(modal_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update handleSaveNewCustomer
old_save_cust = """  const handleSaveNewCustomer = async () => {
    if (!newCustomer.first_name || (newCustomer.phone.length !== 10 && newCustomer.phone.length !== 12)) {
      toast.error('First name and 10 or 12-digit phone number are required');
      return;
    }
    setLoading(true);
    try {
      const res = await axiosClient.post('/customers/', {
        first_name: newCustomer.first_name,
        last_name: newCustomer.last_name,
        phone_number: newCustomer.phone,
        email: null,
        address: newCustomer.address || '',
        city: newCustomer.city || 'Takhatgarh',
        state: 'Rajasthan',
        gst_number: newCustomer.gst_number || null,
        aadhaar_pan: newCustomer.aadhaar_pan || null
      });
      setCustomers([...customers, res.data]);
      setSelectedCustomer(res.data.id);
      setMode('checkout');
      toast.success('Customer added');
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to save customer'));
    } finally {
      setLoading(false);
    }
  };"""

new_save_cust = """  const handleSaveNewCustomer = async () => {
    if (!newCustomer.first_name || !newCustomer.phone || (newCustomer.phone.length !== 10 && newCustomer.phone.length !== 12)) {
      toast.error('First name and 10 or 12-digit phone number are required');
      return;
    }
    setLoading(true);
    try {
      const res = await axiosClient.post('/customers/', {
        first_name: newCustomer.first_name,
        last_name: newCustomer.last_name || '',
        phone_number: newCustomer.phone,
        email: null,
        address: newCustomer.address || '',
        city: newCustomer.city || 'Takhatgarh',
        state: 'Rajasthan',
        gst_number: newCustomer.gst_number || null,
        aadhaar_pan: newCustomer.aadhaar_pan || null
      });
      const saved = res.data;
      setCustomers(prev => {
        const idx = prev.findIndex(c => c.id === saved.id);
        if (idx >= 0) {
          const updated = [...prev];
          updated[idx] = saved;
          return updated;
        }
        return [...prev, saved];
      });
      setSelectedCustomer(saved.id);
      useBillingStore.getState().setSelectedCustomerId(saved.id);
      setBuyerDetails({
        name: `${saved.first_name || ''} ${saved.last_name || ''}`.trim() || 'Customer',
        phone: saved.phone_number || '',
        address: saved.address || '',
        city: saved.city || 'Takhatgarh',
        state: saved.state || 'Rajasthan',
        state_code: saved.state_code || '08',
        place_of_supply: saved.place_of_supply || saved.state || 'Rajasthan',
        gstin: saved.gst_number || '',
        pan: saved.aadhaar_pan || ''
      });
      setMode('checkout');
      toast.success('Customer saved & selected for bill');
    } catch (e: any) {
      toast.error(getErrorMessage(e, 'Failed to save customer'));
    } finally {
      setLoading(false);
    }
  };"""

if old_save_cust in code:
    code = code.replace(old_save_cust, new_save_cust, 1)
    print("handleSaveNewCustomer replaced successfully!")
else:
    print("handleSaveNewCustomer not found!")

# 2. Update select onChange
old_select = """                <select 
                  className="w-full bg-background border border-gray-700 rounded p-2.5 text-sm text-white outline-none focus:border-primary transition-colors mb-3" 
                  value={selectedCustomer} 
                  onChange={e => setSelectedCustomer(e.target.value ? Number(e.target.value) : '')}
                >"""

new_select = """                <select 
                  className="w-full bg-background border border-gray-700 rounded p-2.5 text-sm text-white outline-none focus:border-primary transition-colors mb-3 cursor-pointer" 
                  value={selectedCustomer} 
                  onChange={e => {
                    const id = e.target.value ? Number(e.target.value) : '';
                    setSelectedCustomer(id);
                    useBillingStore.getState().setSelectedCustomerId(id ? Number(id) : null);
                    if (id) {
                      const c = customers.find(x => x.id === id);
                      if (c) {
                        setBuyerDetails({
                          name: `${c.first_name || ''} ${c.last_name || ''}`.trim() || 'Customer',
                          phone: c.phone_number || '',
                          address: c.address || '',
                          city: c.city || 'Takhatgarh',
                          state: c.state || 'Rajasthan',
                          state_code: c.state_code || '08',
                          place_of_supply: c.place_of_supply || c.state || 'Rajasthan',
                          gstin: c.gst_number || '',
                          pan: c.aadhaar_pan || ''
                        });
                      }
                    } else {
                      setBuyerDetails({
                        name: 'Walk-in Customer',
                        phone: '',
                        address: '',
                        city: 'Takhatgarh',
                        state: 'Rajasthan',
                        state_code: '08',
                        place_of_supply: 'Rajasthan',
                        gstin: '',
                        pan: ''
                      });
                    }
                  }}
                >"""

if old_select in code:
    code = code.replace(old_select, new_select, 1)
    print("select onChange replaced successfully!")
else:
    print("select onChange not found!")

with open(modal_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Saved CheckoutModal.tsx")
