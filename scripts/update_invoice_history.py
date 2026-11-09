with open('frontend/src/pages/invoices/InvoiceHistory.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update header
text = text.replace(
    "{currentCompanyId === 2 ? '💎 Pride Gold (GST)' : '🏛️ Saideep Jewellers (Normal)'}",
    "{currentCompanyId === 2 ? '💎 SAIDEEP JEWELLERS (GST)' : '🏛️ SAIDEEP JEWELLERS (Normal)'}"
)
text = text.replace(
    "Viewing strictly isolated {currentCompanyId === 2 ? 'GST Tax Invoices for Pride Gold' : 'invoices for Saideep Jewellers'}",
    "Viewing strictly isolated {currentCompanyId === 2 ? 'GST Tax Invoices for Saideep Jewellers' : 'retail non-GST invoices for Saideep Jewellers'}"
)

# 2. Update actions: remove && tab === 'sales'
old_tab_action = "{invoice.status !== 'Cancelled' && tab === 'sales' && ("
new_tab_action = "{invoice.status !== 'Cancelled' && ("
assert old_tab_action in text, "old_tab_action not found"
text = text.replace(old_tab_action, new_tab_action, 1)

# 3. Update handleDelete
old_handle_delete = """  const handleDelete = async (invoice: Invoice) => {

    if (!confirm(`Are you sure you want to cancel invoice ${invoice.invoice_number}?`)) {

      return;

    }



    try {

      const isExchange = invoice.invoice_number.startsWith('EXC-');

      const isPurchase = invoice.invoice_number.startsWith('PUR-');

      const endpoint = isPurchase ? `/purchases/${invoice.id}` : isExchange ? `/exchanges/${invoice.id}` : `/invoices/${invoice.id}`;"""

new_handle_delete = """  const handleDelete = async (invoice: Invoice) => {
    const isExchange = invoice.invoice_number.startsWith('EXC-');
    const isPurchase = invoice.invoice_number.startsWith('PUR-');
    const billType = isPurchase ? 'purchase bill' : isExchange ? 'exchange bill' : 'invoice';

    if (!confirm(`Are you sure you want to delete ${billType} ${invoice.invoice_number}? This will reverse stock and ledger balances.`)) {
      return;
    }

    try {
      const endpoint = isPurchase ? `/purchases/${invoice.id}` : isExchange ? `/exchanges/${invoice.id}` : `/invoices/${invoice.id}`;"""

assert old_handle_delete in text, "old_handle_delete not found"
text = text.replace(old_handle_delete, new_handle_delete, 1)

# Update success toast
text = text.replace(
    "toast.success('Invoice cancelled and PDF removed from vault successfully');",
    "toast.success(`${isPurchase ? 'Purchase bill' : isExchange ? 'Exchange bill' : 'Invoice'} deleted and removed from vault successfully`);"
)

with open('frontend/src/pages/invoices/InvoiceHistory.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated InvoiceHistory.tsx successfully!")
