import re

with open('src/screens/inventory/InventoryScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# Fix duplicates
target_duplicate = """            <View style={{ marginLeft: 12, justifyContent: 'center' }}>
              <TouchableOpacity style={{ padding: 4 }} onPress={() => navigation.navigate('EditInventory', { item })}>
                <Ionicons name="pencil" size={18} color="#ccc" />
              </TouchableOpacity>
            </View>
          </View>
            <View style={{ marginLeft: 12, justifyContent: 'center' }}>
              <TouchableOpacity style={{ padding: 4 }} onPress={() => navigation.navigate('EditInventory', { item })}>
                <Ionicons name="pencil" size={18} color="#ccc" />
              </TouchableOpacity>
            </View>"""

replacement = """            <View style={{ marginLeft: 12, justifyContent: 'center' }}>
              <TouchableOpacity style={{ padding: 4 }} onPress={() => navigation.navigate('EditInventory', { item })}>
                <Ionicons name="pencil" size={20} color="#888" />
              </TouchableOpacity>
            </View>
          """

txt = txt.replace(target_duplicate, replacement)

# If it didn't match that exact string because of whitespace, let's just use regex to strip all pencil blocks and add one cleanly
txt = re.sub(r'<View style=\{\{ marginLeft: 12, justifyContent: \'center\' \}\}>.*?</TouchableOpacity>\s*</View>', '', txt, flags=re.DOTALL)

clean_replacement = """              </Text>
            </View>
            <View style={{ marginLeft: 12, justifyContent: 'center' }}>
              <TouchableOpacity style={{ padding: 8 }} onPress={() => navigation.navigate('EditInventory', { item })}>
                <Ionicons name="pencil" size={20} color="#d4af37" />
              </TouchableOpacity>
            </View>"""
txt = txt.replace('              </Text>\n            </View>', clean_replacement)


with open('src/screens/inventory/InventoryScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
