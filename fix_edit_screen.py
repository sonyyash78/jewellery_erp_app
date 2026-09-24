import re

with open('src/screens/inventory/EditInventoryScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace('export default function CreateInventoryScreen({ navigation }: any) {', 'export default function EditInventoryScreen({ route, navigation }: any) {\n  const { item } = route.params || {};')

# Update state initialization
state_init = """  const [formData, setFormData] = useState({
    item_name: item?.item_name || '',
    category: item?.category || '',
    metal: item?.metal || 'Gold',
    purity: item?.purity || '',
    hsn: item?.hsn || '',
    gross_weight: item?.gross_weight?.toString() || '',
    stone_weight: item?.stone_weight?.toString() || '',
    net_weight: item?.net_weight?.toString() || '',
    tanch: item?.tanch?.toString() || '',
    wastage: item?.wastage?.toString() || '',
    making_type: item?.making_type || 'Flat',
    making_charge: item?.making_charge?.toString() || '',
    hallmark: item?.hallmark?.toString() || '',
    other_charges: item?.other_charges?.toString() || '',
    location: item?.location || '',
    shelf: item?.shelf || '',
    status: item?.status || 'Available',
    description: item?.description || ''
  });"""

txt = re.sub(r'  const \[formData, setFormData\] = useState\(\{.*?\}\);', state_init, txt, flags=re.DOTALL)

# Update submit handler
submit_replace = """    try {
      setLoading(true);
      await axiosClient.put(`/stock/${item.id}`, {"""
txt = txt.replace("""    try {
      setLoading(true);
      await axiosClient.post('/stock/', {""", submit_replace)

txt = txt.replace("Alert.alert('Success', 'Inventory item added successfully!');", "Alert.alert('Success', 'Inventory item updated successfully!');")
txt = txt.replace("'Failed to add item to inventory.'", "'Failed to update inventory item.'")
txt = txt.replace("console.log('Failed to create item',", "console.log('Failed to update item',")

txt = txt.replace(">Save Item & Generate QR<", ">Save Changes<")

with open('src/screens/inventory/EditInventoryScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
