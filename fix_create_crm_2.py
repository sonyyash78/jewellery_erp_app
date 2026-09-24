import re

with open('src/screens/crm/CreateCRMScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# Make sure we don't crash if `item` is not passed in route.params when pressing ADD CUSTOMER
init_state_fix = """export default function CreateCRMScreen({ route, navigation }: any) {
  const { type, item } = route.params || {}; // 'Customer' or 'Supplier'
  
  const [formData, setFormData] = useState({
    name: item ? (item.first_name || item.name || '') : '',
    mobile: item ? (item.phone_number || item.mobile || '') : '',
    address: item?.address || '',
    aadhaar_pan: item?.aadhaar_pan || '',
    gst_number: item?.gst_number || ''
  });"""

txt = re.sub(
    r"export default function CreateCRMScreen\(\{ route, navigation \}: any\) \{[\s\S]*?gst_number: item\?\.gst_number \|\| ''\n  \}\);", 
    init_state_fix, 
    txt
)
if "const { type, item } = route.params || {};" not in txt:
    txt = re.sub(
        r"export default function CreateCRMScreen\(\{ route, navigation \}: any\) \{[\s\S]*?gst_number: ''\n  \}\);", 
        init_state_fix, 
        txt
    )

new_submit = """  const handleSubmit = async () => {
    if (!formData.name || !formData.mobile) {
      Alert.alert('Validation Error', 'Name and Mobile Number are required.');
      return;
    }

    // Must be exactly 10 digits
    if (formData.mobile.length !== 10) {
      Alert.alert('Validation Error', 'Mobile Number must be exactly 10 digits.');
      return;
    }

    try {
      setLoading(true);
      if (type === 'Supplier') {
        const payload = {
          name: formData.name,
          mobile: formData.mobile,
          address: formData.address || undefined,
          gst_number: formData.gst_number || undefined,
        };
        if (item && item.id) {
          await axiosClient.put(`/suppliers/${item.id}`, payload);
        } else {
          await axiosClient.post('/suppliers/', payload);
        }
      } else {
        const payload = {
          first_name: formData.name,
          phone_number: formData.mobile,
          address: formData.address || undefined,
          aadhaar_pan: formData.aadhaar_pan || undefined,
          gst_number: formData.gst_number || undefined
        };
        if (item && item.id) {
          await axiosClient.put(`/customers/${item.id}`, payload);
        } else {
          await axiosClient.post('/customers/', payload);
        }
      }
      
      Alert.alert('Success', `${type} saved successfully!`);
      navigation.goBack();
    } catch (error: any) {
      console.log(`Failed to save ${type}`, error.response?.data || error.message);
      Alert.alert('Error', `Failed to save ${type}. Please check your inputs.`);
    } finally {
      setLoading(false);
    }
  };"""

txt = re.sub(
    r"  const handleSubmit = async \(\) => \{[\s\S]*?    \} finally \{\n      setLoading\(false\);\n    \}\n  \};",
    new_submit,
    txt
)

with open('src/screens/crm/CreateCRMScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
