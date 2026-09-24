import re

with open('src/screens/inventory/InventoryScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# Replace any sequence of closing views after fineWtText
pattern = r'(Fine: \{fineWt\}g \(\{item\.tanch \|\| 0\}% \+ \{item\.wastage \|\| 0\}%\)\s*</Text>\s*</View>)\s*</View>\s*</View>\s*</View>'
replacement = r"""\1
              <View style={{ marginLeft: 12, justifyContent: 'center' }}>
                <TouchableOpacity style={{ padding: 8 }} onPress={() => navigation.navigate('EditInventory', { item })}>
                  <Ionicons name="pencil" size={20} color="#d4af37" />
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </View>"""

txt = re.sub(pattern, replacement, txt)

with open('src/screens/inventory/InventoryScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
