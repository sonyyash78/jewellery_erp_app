import re

with open('src/screens/inventory/InventoryScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

duplicate_block = """            <View style={{ marginLeft: 12, justifyContent: 'center' }}>
              <TouchableOpacity style={{ padding: 8 }} onPress={() => navigation.navigate('EditInventory', { item })}>
                <Ionicons name="pencil" size={20} color="#d4af37" />
              </TouchableOpacity>
            </View>
            <View style={{ marginLeft: 12, justifyContent: 'center' }}>
              <TouchableOpacity style={{ padding: 8 }} onPress={() => navigation.navigate('EditInventory', { item })}>
                <Ionicons name="pencil" size={20} color="#d4af37" />
              </TouchableOpacity>
            </View>"""

single_block = """            <View style={{ marginLeft: 12, justifyContent: 'center' }}>
              <TouchableOpacity style={{ padding: 8 }} onPress={() => navigation.navigate('EditInventory', { item })}>
                <Ionicons name="pencil" size={20} color="#d4af37" />
              </TouchableOpacity>
            </View>"""

txt = txt.replace(duplicate_block, single_block)

# Just in case they are separated by spaces differently, let's use regex to guarantee there's only one.
blocks = re.findall(r'<View style=\{\{ marginLeft: 12, justifyContent: \'center\' \}\}>.*?<\/TouchableOpacity>\s*<\/View>', txt, flags=re.DOTALL)
if len(blocks) > 1:
    txt = txt.replace(blocks[0], '')

with open('src/screens/inventory/InventoryScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
