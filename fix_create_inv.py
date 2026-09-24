import re

with open('src/screens/inventory/CreateInventoryScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

target = """            <View style={styles.col}>
              <Text style={styles.label}>STATUS</Text>
              <TextInput style={styles.input} value={formData.status} onChangeText={(t) => setFormData({ ...formData, status: t })} />
            </View>"""

replacement = """          </View>
          
          <Text style={styles.label}>STATUS</Text>
          <View style={[styles.radioGroup, { marginBottom: 16 }]}>
            <TouchableOpacity style={[styles.radio, formData.status === 'Available' && styles.radioActive]} onPress={() => setFormData({ ...formData, status: 'Available' })}>
              <Text style={[styles.radioText, {fontSize: 11}]} numberOfLines={1}>Available</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.radio, formData.status === 'Low Stock' && styles.radioActive]} onPress={() => setFormData({ ...formData, status: 'Low Stock' })}>
              <Text style={[styles.radioText, {fontSize: 11}]} numberOfLines={1}>Low Stock</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.radio, formData.status === 'Not Available' && styles.radioActive]} onPress={() => setFormData({ ...formData, status: 'Not Available' })}>
              <Text style={[styles.radioText, {fontSize: 11}]} numberOfLines={1}>Not Available</Text>
            </TouchableOpacity>
          </View>"""

# Fix the structural row closing since we pulled it out of the 3-col row
# Current:
#               <TextInput style={styles.input} placeholder="e.g. Tray 5" placeholderTextColor="#555" value={formData.shelf} onChangeText={(t) => setFormData({ ...formData, shelf: t })} />
#             </View>
#             <View style={styles.col}>
#               <Text style={styles.label}>STATUS</Text>
#               <TextInput style={styles.input} value={formData.status} onChangeText={(t) => setFormData({ ...formData, status: t })} />
#             </View>
#           </View>

txt = txt.replace(
"""            <View style={styles.col}>
              <Text style={styles.label}>STATUS</Text>
              <TextInput style={styles.input} value={formData.status} onChangeText={(t) => setFormData({ ...formData, status: t })} />
            </View>
          </View>""",
replacement
)

if txt.find('Low Stock') != -1:
    with open('src/screens/inventory/CreateInventoryScreen.tsx', 'w', encoding='utf-8') as f:
        f.write(txt)
    print('Updated CreateInventoryScreen')
else:
    print('Failed to replace')
