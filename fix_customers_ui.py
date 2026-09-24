import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# Add formatAmount function inside CustomersScreen component
format_func = """
  const formatAmount = (num: number) => {
    if (!num) return '0';
    const absNum = Math.abs(num);
    let formatted = '';
    if (absNum >= 10000000) {
      formatted = (absNum / 10000000).toFixed(2) + 'Cr';
    } else if (absNum >= 100000) {
      formatted = (absNum / 100000).toFixed(2) + 'L';
    } else if (absNum >= 1000) {
      formatted = (absNum / 1000).toFixed(2) + 'K';
    } else {
      formatted = absNum.toFixed(2);
    }
    formatted = formatted.replace(/\.00([a-zA-Z]*)$/, '$1'); // clean up trailing .00
    return (num < 0 ? '-' : '') + formatted;
  };
"""

txt = txt.replace('  const totalCustomers = customers.length;', format_func + '\n  const totalCustomers = customers.length;')

# Replace toLocaleString formatting with formatAmount
txt = txt.replace(
    "₹ {(item.outstanding_balance || 0).toLocaleString('en-IN')}",
    "₹ {formatAmount(item.outstanding_balance || 0)}"
)
txt = txt.replace(
    "₹ {(item.credit_limit || 0).toLocaleString('en-IN')}",
    "₹ {formatAmount(item.credit_limit || 0)}"
)
txt = txt.replace(
    "₹ {netOutstanding.toLocaleString('en-IN')}",
    "₹ {formatAmount(netOutstanding)}"
)

# Fix summary label wrapping/size to make it look even better on small screens
txt = txt.replace(
    '<Text style={styles.summaryValueBig}>₹ {formatAmount(netOutstanding)}</Text>',
    '<Text style={styles.summaryValueBig} numberOfLines={1} adjustsFontSizeToFit>₹ {formatAmount(netOutstanding)}</Text>'
)

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
