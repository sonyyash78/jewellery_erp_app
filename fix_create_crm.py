import re

with open('src/screens/crm/CreateCRMScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# Make it support item prefilling
init_state = """  const { type, item } = route.params; // 'Customer' or 'Supplier'
  
  const [formData, setFormData] = useState({
    name: item ? (item.first_name || item.name || '') : '',
    mobile: item ? (item.phone_number || item.mobile || '') : '',
    address: item?.address || '',
    aadhaar_pan: item?.aadhaar_pan || '',
    gst_number: item?.gst_number || ''
  });"""

txt = re.sub(r"  const \{ type \} = route\.params;.*?gst_number: ''\n  \}\);", init_state, txt, flags=re.DOTALL)

# Update submit logic to support PUT
submit_replace = """    try {
      setLoading(true);
      if (type === 'Supplier') {
        const payload = {
          name: formData.name,
          mobile: formData.mobile,
          address: formData.address || undefined,
          gst_number: formData.gst_number || undefined,
          aadhaar_pan: formData.aadhaar_pan || undefined,
        };
        if (item) {
          await axiosClient.put(`/suppliers/${item.id}`, payload);
        } else {
          await axiosClient.post('/suppliers/', payload);
        }
      } else {
        const payload = {
          first_name: formData.name,
          phone_number: formData.mobile,
          address: formData.address || undefined,
          gst_number: formData.gst_number || undefined,
          aadhaar_pan: formData.aadhaar_pan || undefined,
        };
        if (item) {
          await axiosClient.put(`/customers/${item.id}`, payload);
        } else {
          await axiosClient.post('/customers/', payload);
        }
      }
      Alert.alert('Success', `${type} saved successfully!`);"""

txt = re.sub(r"    try \{\n      setLoading\(true\);\n      if \(type === 'Supplier'\) \{.*?Alert\.alert\('Success', `\$\{type\} added successfully!`\);", submit_replace, txt, flags=re.DOTALL)

with open('src/screens/crm/CreateCRMScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
