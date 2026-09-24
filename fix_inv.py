import re

with open('src/screens/inventory/InventoryScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# Fix summary label text wrapping and layout
txt = txt.replace(
    '<View>\n            <Text style={styles.summaryLabel}>TOTAL ITEMS</Text>\n            <Text style={styles.summaryValue}>{totalItems}</Text>\n          </View>',
    '<View style={{ flex: 1, flexShrink: 1 }}>\n            <Text style={styles.summaryLabel} numberOfLines={2}>TOTAL ITEMS</Text>\n            <Text style={styles.summaryValue} adjustsFontSizeToFit numberOfLines={1}>{totalItems}</Text>\n          </View>'
)

txt = txt.replace(
    '<View>\n            <Text style={styles.summaryLabel}>TOTAL WEIGHT (NET)</Text>\n            <Text style={styles.summaryValue}>{totalWeight.toFixed(3)}g</Text>\n          </View>',
    '<View style={{ flex: 1, flexShrink: 1 }}>\n            <Text style={styles.summaryLabel} numberOfLines={2}>TOTAL WEIGHT (NET)</Text>\n            <Text style={styles.summaryValue} adjustsFontSizeToFit numberOfLines={1}>{totalWeight.toFixed(3)}g</Text>\n          </View>'
)

# Fix summary icon box size to save space
txt = txt.replace('width: 36,\n    height: 36,\n    borderRadius: 18,', 'width: 32,\n    height: 32,\n    borderRadius: 16,')
txt = txt.replace('marginRight: 12,', 'marginRight: 8,')

# Add new status badge logic
txt = txt.replace(
    "const isAvailable = item.status === 'Available';",
    "const isAvailable = item.status === 'Available';\n    const isLowStock = item.status === 'Low Stock';\n    const statusBadgeStyle = isAvailable ? styles.statusAvailable : (isLowStock ? styles.statusLowStock : styles.statusSold);\n    const statusTextStyle = isAvailable ? styles.statusTextAvailable : (isLowStock ? styles.statusTextLowStock : styles.statusTextSold);"
)

txt = txt.replace(
    "<View style={[styles.statusBadge, isAvailable ? styles.statusAvailable : styles.statusSold]}>\n              <Text style={isAvailable ? styles.statusTextAvailable : styles.statusTextSold}>\n                {item.status}\n              </Text>\n            </View>",
    "<View style={[styles.statusBadge, statusBadgeStyle]}>\n              <Text style={statusTextStyle}>\n                {item.status || 'Not Available'}\n              </Text>\n            </View>"
)

# Add Low Stock styles
styles_to_add = """
  statusLowStock: {
    backgroundColor: 'rgba(234, 179, 8, 0.1)',
    borderColor: 'rgba(234, 179, 8, 0.3)',
  },
  statusTextLowStock: {
    color: '#eab308',
    fontSize: 10,
    fontWeight: 'bold',
  },
"""

txt = txt.replace('  statusSold: {', styles_to_add + '  statusSold: {')

with open('src/screens/inventory/InventoryScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
