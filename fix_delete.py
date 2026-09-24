import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# Add Alert to imports
if 'Alert' not in txt:
    txt = txt.replace('import { View,', 'import { Alert, View,')

# Add delete function inside the component
delete_func = """
  const handleDelete = (id: number, type: string) => {
    Alert.alert(
      `Delete ${type}`,
      `Are you sure you want to delete this ${type.toLowerCase()}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: async () => {
            try {
              const endpoint = type === 'Customer' ? `/customers/${id}` : `/suppliers/${id}`;
              await axiosClient.delete(endpoint);
              fetchCRMData(search); // refresh list
            } catch (error) {
              Alert.alert('Error', `Failed to delete ${type.toLowerCase()}`);
            }
          }
        }
      ]
    );
  };
"""

txt = txt.replace('const currentData = activeTab === \'customers\' ? customers : suppliers;', delete_func + '\n  const currentData = activeTab === \'customers\' ? customers : suppliers;')

# Update the delete button
old_btn = '<TouchableOpacity style={[styles.actionBtn, styles.deleteBtn]}>'
new_btn = '<TouchableOpacity style={[styles.actionBtn, styles.deleteBtn]} onPress={() => handleDelete(item.id, isCustomer ? "Customer" : "Supplier")}>'
txt = txt.replace(old_btn, new_btn)

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
