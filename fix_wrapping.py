import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace(
    '<Text style={styles.summaryValueBig}>₹ {formatAmount(netOutstanding)}</Text>',
    '<Text style={styles.summaryValueBig} numberOfLines={1} adjustsFontSizeToFit>₹ {formatAmount(netOutstanding)}</Text>'
)

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
