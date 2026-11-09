import os

chk_modal_path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\CheckoutModal.tsx"
with open(chk_modal_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update imports
if "Users, MapPin" not in content:
    content = content.replace("import { Check, X, Calculator, UserPlus } from 'lucide-react';",
                              "import { Check, X, Calculator, UserPlus, Users, MapPin } from 'lucide-react';")

# 2. Add buyerDetails state and update newCustomer state
old_cust_state = "const [newCustomer, setNewCustomer] = useState({ first_name: '', last_name: '', phone: '', city: '' });"
new_cust_state = """const [newCustomer, setNewCustomer] = useState({ first_name: '', last_name: '', phone: '', city: '', address: '', gst_number: '', aadhaar_pan: '' });

  const [buyerDetails, setBuyerDetails] = useState({
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

  useEffect(() => {
    if (selectedCustomer) {
      const c = customers.find(x => x.id === selectedCustomer);
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
  }, [selectedCustomer, customers]);"""

if old_cust_state in content:
    content = content.replace(old_cust_state, new_cust_state)
    print("Added buyerDetails state & sync effect in CheckoutModal.tsx")

# 3. Update handleSaveNewCustomer to pass address, gst_number, aadhaar_pan
old_save_cust = """      const res = await axiosClient.post('/customers/', {
        first_name: newCustomer.first_name,
        last_name: newCustomer.last_name,
        phone_number: newCustomer.phone,
        email: null,
        address: '',
        city: newCustomer.city
      });"""

new_save_cust = """      const res = await axiosClient.post('/customers/', {
        first_name: newCustomer.first_name,
        last_name: newCustomer.last_name,
        phone_number: newCustomer.phone,
        email: null,
        address: newCustomer.address || '',
        city: newCustomer.city || 'Takhatgarh',
        state: 'Rajasthan',
        gst_number: newCustomer.gst_number || null,
        aadhaar_pan: newCustomer.aadhaar_pan || null
      });"""

if old_save_cust in content:
    content = content.replace(old_save_cust, new_save_cust)
    print("Updated handleSaveNewCustomer payload in CheckoutModal.tsx")

# 4. Update finalPayload in handleGenerate to send buyer details
old_payload_part = """      customer_id: selectedCustomer || null,
      status: isFullySettled ? 'Paid' : 'Completed',"""

new_payload_part = """      customer_id: selectedCustomer || null,
      buyer_name: buyerDetails.name,
      buyer_phone: buyerDetails.phone,
      buyer_address: buyerDetails.address,
      buyer_city: buyerDetails.city,
      buyer_state: buyerDetails.state,
      buyer_state_code: buyerDetails.state_code,
      buyer_place_of_supply: buyerDetails.place_of_supply,
      buyer_gstin: buyerDetails.gstin,
      buyer_pan: buyerDetails.pan,
      status: isFullySettled ? 'Paid' : 'Completed',"""

if old_payload_part in content:
    content = content.replace(old_payload_part, new_payload_part)
    print("Updated finalPayload with buyer details in CheckoutModal.tsx")

# 5. Replace Section 3 Customer selection with Editable Buyer Card
old_sec3 = """              {/* SECTION 3: Customer */}
              <div className="border-t border-gray-800 pt-4">
                <div className="flex justify-between items-end mb-2">
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest">Select Customer</label>
                  <button onClick={() => setMode('new_customer')} className="text-[10px] bg-primary/20 text-primary px-2 py-1 rounded flex items-center gap-1 hover:bg-primary/30 transition-colors"><UserPlus size={12} /> New</button>
                </div>
                <select className="w-full bg-background border border-gray-700 rounded p-3 text-white outline-none focus:border-primary transition-colors" value={selectedCustomer} onChange={e => setSelectedCustomer(Number(e.target.value))}>
                  <option value="">-- Walk-in Customer --</option>
                  {customers.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name || ''} ({c.phone_number})</option>)}
                </select>
                {!isFullySettled && !selectedCustomer && <p className="text-red-400 text-[10px] mt-1">* A customer must be selected for outstanding balances.</p>}
              </div>"""

new_sec3 = """              {/* SECTION 3: Customer & Buyer Details (बिल क्रेता विवरण) */}
              <div className="border-t border-gray-800 pt-4">
                <div className="flex justify-between items-end mb-2">
                  <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
                    <Users size={14} className="text-primary" />
                    Buyer / Customer Details (क्रेता विवरण)
                  </label>
                  <button type="button" onClick={() => setMode('new_customer')} className="text-[10px] bg-primary/20 text-primary px-2.5 py-1 rounded flex items-center gap-1 hover:bg-primary/30 transition-colors font-bold">
                    <UserPlus size={12} /> + New Customer
                  </button>
                </div>
                
                <select 
                  className="w-full bg-background border border-gray-700 rounded p-2.5 text-sm text-white outline-none focus:border-primary transition-colors mb-3" 
                  value={selectedCustomer} 
                  onChange={e => setSelectedCustomer(e.target.value ? Number(e.target.value) : '')}
                >
                  <option value="">-- Walk-in / Cash Customer --</option>
                  {customers.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name || ''} ({c.phone_number})</option>)}
                </select>

                {/* EDITABLE BUYER CARD */}
                <div className="bg-[#14141B] border border-gray-800 rounded-xl p-3 space-y-2.5">
                  <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider flex justify-between items-center pb-1.5 border-b border-gray-800">
                    <span className="flex items-center gap-1.5 text-white">
                      <MapPin size={13} className="text-amber-400" />
                      Editable Buyer Details (बिल पर छपने वाला नाम व पता)
                    </span>
                    <span className="text-[10px] text-primary lowercase font-normal">* editable for this bill</span>
                  </div>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <div>
                      <label className="block text-[10px] text-gray-400 uppercase font-semibold mb-0.5">Buyer Name</label>
                      <input 
                        type="text"
                        value={buyerDetails.name}
                        onChange={e => setBuyerDetails({ ...buyerDetails, name: e.target.value })}
                        placeholder="Customer / Buyer Name"
                        className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary font-medium"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] text-gray-400 uppercase font-semibold mb-0.5">Contact Phone</label>
                      <input 
                        type="text"
                        value={buyerDetails.phone}
                        onChange={e => setBuyerDetails({ ...buyerDetails, phone: e.target.value })}
                        placeholder="Phone Number"
                        className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[10px] text-gray-400 uppercase font-semibold mb-0.5">
                      Buyer Address (क्रेता का पूरा पता - Editable)
                    </label>
                    <input 
                      type="text"
                      value={buyerDetails.address}
                      onChange={e => setBuyerDetails({ ...buyerDetails, address: e.target.value })}
                      placeholder="e.g. 167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912"
                      className="w-full bg-background border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white outline-none focus:border-primary font-medium"
                    />
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    <div>
                      <label className="block text-[10px] text-gray-400 uppercase font-semibold mb-0.5">Place of Supply</label>
                      <input 
                        type="text"
                        value={buyerDetails.place_of_supply}
                        onChange={e => setBuyerDetails({ ...buyerDetails, place_of_supply: e.target.value })}
                        placeholder="State"
                        className="w-full bg-background border border-gray-700 rounded px-2 py-1.5 text-xs text-white outline-none focus:border-primary"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] text-gray-400 uppercase font-semibold mb-0.5">State Code</label>
                      <input 
                        type="text"
                        value={buyerDetails.state_code}
                        onChange={e => setBuyerDetails({ ...buyerDetails, state_code: e.target.value })}
                        placeholder="08"
                        className="w-full bg-background border border-gray-700 rounded px-2 py-1.5 text-xs text-white outline-none focus:border-primary font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] text-gray-400 uppercase font-semibold mb-0.5">Buyer GSTIN</label>
                      <input 
                        type="text"
                        value={buyerDetails.gstin}
                        onChange={e => setBuyerDetails({ ...buyerDetails, gstin: e.target.value.toUpperCase() })}
                        placeholder="Optional for B2B"
                        className="w-full bg-background border border-gray-700 rounded px-2 py-1.5 text-xs text-white outline-none focus:border-primary font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] text-gray-400 uppercase font-semibold mb-0.5">Buyer PAN</label>
                      <input 
                        type="text"
                        value={buyerDetails.pan}
                        onChange={e => setBuyerDetails({ ...buyerDetails, pan: e.target.value.toUpperCase() })}
                        placeholder="Optional"
                        className="w-full bg-background border border-gray-700 rounded px-2 py-1.5 text-xs text-white outline-none focus:border-primary font-mono"
                      />
                    </div>
                  </div>
                </div>

                {!isFullySettled && !selectedCustomer && <p className="text-red-400 text-[10px] mt-1">* A customer must be selected for outstanding balances.</p>}
              </div>"""

if old_sec3 in content:
    content = content.replace(old_sec3, new_sec3)
    print("Replaced Section 3 with Editable Buyer Card in CheckoutModal.tsx")

# 6. Replace mode === 'new_customer' form
old_new_cust_form = """          {mode === 'new_customer' && (
            <div className="space-y-4">
              <h3 className="font-bold text-white mb-4 border-b border-gray-800 pb-2">Add New Customer</h3>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">First Name *</label>
                <input placeholder="First Name" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newCustomer.first_name} onChange={e => setNewCustomer({ ...newCustomer, first_name: e.target.value })} />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Last Name</label>
                <input placeholder="Last Name" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newCustomer.last_name} onChange={e => setNewCustomer({ ...newCustomer, last_name: e.target.value })} />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Phone Number *</label>
                <input placeholder="Phone Number" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newCustomer.phone} onChange={e => setNewCustomer({ ...newCustomer, phone: e.target.value })} />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">City</label>
                <input placeholder="City" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary" value={newCustomer.city} onChange={e => setNewCustomer({ ...newCustomer, city: e.target.value })} />
              </div>
              <div className="flex space-x-3 mt-6">
                <button onClick={() => setMode('checkout')} className="flex-1 py-2 border border-gray-700 rounded text-gray-400 hover:bg-gray-800">Cancel</button>
                <button onClick={handleSaveNewCustomer} disabled={loading} className="flex-1 py-2 bg-primary text-black font-bold rounded hover:bg-primary/90">{loading ? 'Saving...' : 'Save Customer'}</button>
              </div>
            </div>
          )}"""

new_new_cust_form = """          {mode === 'new_customer' && (
            <div className="space-y-3">
              <h3 className="font-bold text-white mb-2 border-b border-gray-800 pb-2 flex items-center gap-2">
                <UserPlus size={16} className="text-primary" />
                Add New Customer
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">First Name *</label>
                  <input placeholder="First Name" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary text-xs" value={newCustomer.first_name} onChange={e => setNewCustomer({ ...newCustomer, first_name: e.target.value })} />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Last Name</label>
                  <input placeholder="Last Name" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary text-xs" value={newCustomer.last_name} onChange={e => setNewCustomer({ ...newCustomer, last_name: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Phone Number *</label>
                  <input placeholder="Phone Number" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary text-xs" value={newCustomer.phone} onChange={e => setNewCustomer({ ...newCustomer, phone: e.target.value })} />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">City</label>
                  <input placeholder="City" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary text-xs" value={newCustomer.city} onChange={e => setNewCustomer({ ...newCustomer, city: e.target.value })} />
                </div>
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Address (क्रेता का पता)</label>
                <input placeholder="Full Address" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary text-xs" value={newCustomer.address} onChange={e => setNewCustomer({ ...newCustomer, address: e.target.value })} />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">GSTIN Number (Optional)</label>
                  <input placeholder="e.g. 08XXXXX..." className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary text-xs font-mono" value={newCustomer.gst_number} onChange={e => setNewCustomer({ ...newCustomer, gst_number: e.target.value.toUpperCase() })} />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">PAN Number (Optional)</label>
                  <input placeholder="e.g. ABCDE1234F" className="w-full bg-background border border-gray-700 rounded p-2 text-white outline-none focus:border-primary text-xs font-mono" value={newCustomer.aadhaar_pan} onChange={e => setNewCustomer({ ...newCustomer, aadhaar_pan: e.target.value.toUpperCase() })} />
                </div>
              </div>
              <div className="flex space-x-3 mt-4 pt-2 border-t border-gray-800">
                <button type="button" onClick={() => setMode('checkout')} className="flex-1 py-2 border border-gray-700 rounded text-gray-400 hover:bg-gray-800 text-xs font-bold">Cancel</button>
                <button type="button" onClick={handleSaveNewCustomer} disabled={loading} className="flex-1 py-2 bg-primary text-black font-bold rounded hover:bg-primary/90 text-xs">{loading ? 'Saving...' : 'Save Customer'}</button>
              </div>
            </div>
          )}"""

if old_new_cust_form in content:
    content = content.replace(old_new_cust_form, new_new_cust_form)
    print("Replaced Add New Customer form with address/GST/PAN in CheckoutModal.tsx")

with open(chk_modal_path, "w", encoding="utf-8") as f:
    f.write(content)

print("CheckoutModal.tsx updated successfully!")
