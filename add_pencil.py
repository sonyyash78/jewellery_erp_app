import re

with open('src/screens/inventory/InventoryScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

target = """              </View>
              
              
            </View>"""

replacement = """              </View>
              <View style={{ marginLeft: 12, justifyContent: 'center' }}>
                <TouchableOpacity style={{ padding: 8 }} onPress={() => navigation.navigate('EditInventory', { item })}>
                  <Ionicons name="pencil" size={20} color="#d4af37" />
                </TouchableOpacity>
              </View>
            </View>"""

txt = txt.replace(target, replacement)

with open('src/screens/inventory/InventoryScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
