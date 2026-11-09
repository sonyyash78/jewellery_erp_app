with open('frontend/src/utils/invoicePdfUtils.ts', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect where "const isPrideGold = Boolean(" occurs
idx = text.find("const isPrideGold = Boolean(")
print("Found isPrideGold at:", idx)

# Find the closing ");" for isPrideGold
idx_end = text.find(");", idx)
print("Found closing at:", idx_end)

old_snippet = text[idx:idx_end+2]
print("Old snippet:\n", repr(old_snippet))

new_snippet = """const isGstCompany = Boolean(
      company.gst_enabled === true ||
      data.company?.gst_enabled === true ||
      data.company?.id === 2 ||
      (data as any).company_id === 2 ||
      company.name?.toUpperCase().includes('PRIDE') ||
      String(data.invoice?.invoice_number || '').startsWith('PG/') ||
      String(data.invoice?.invoice_number || '').startsWith('SJ/S/')
    );
    const isPrideGold = isGstCompany;"""

text = text[:idx] + new_snippet + text[idx_end+2:]

# Now replace seller and buyer in gstPayload
s_idx = text.find("seller: {")
b_end = text.find("items: gstItems,", s_idx)
print("seller starts at:", s_idx, "items starts at:", b_end)

new_parties = """seller: (() => {
          const isPurchase = (data as any).type === 'purchase' || String(data.invoice?.invoice_number || '').startsWith('PUR-');
          if (isPurchase) {
            const sp = (data as any).seller || data.customer || {};
            return {
              name: sp.name || 'PRIDE GOLD',
              address: sp.address || '1st Floor, Near Koira Ji ka Bera, Ghodo ka Chowk, Sojati Gate, Jodhpur (Raj.)- 342001',
              city: sp.city || 'Jodhpur',
              state: sp.state || 'Rajasthan',
              state_code: sp.state_code || '08',
              gstin: sp.gstin || '08AEZPK5007N1ZS',
              pan: sp.pan || 'AEZPK5007N',
              phone: sp.phone || '0291-2640999, +91-9929562800',
              email: sp.email || 'info.pridegoldjdr@gmail.com',
              jurisdiction_city: sp.city || 'JODHPUR',
              declaration: 'We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.',
              stamp_url: company.stamp_url,
              signature_url: company.signature_url
            };
          }
          return {
            name: company.name || 'SAIDEEP JEWELLERS',
            address: company.address || '167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912',
            city: company.city || 'Takhatgarh',
            state: company.state || 'Rajasthan',
            state_code: sellerStateCode,
            gstin: company.gstin || '08BNUPK1610E1Z3',
            pan: company.pan || 'BNUPK1610E',
            phone: company.phone || '+91-9460820878',
            email: company.email || 'saideepjewellers78@gmail.com',
            jurisdiction_city: company.jurisdiction_city || 'PALI',
            declaration: company.declaration,
            stamp_url: company.stamp_url,
            signature_url: company.signature_url
          };
        })(),
        buyer: (() => {
          const isPurchase = (data as any).type === 'purchase' || String(data.invoice?.invoice_number || '').startsWith('PUR-');
          if (isPurchase) {
            return {
              name: company.name || 'Saideep Jewellers',
              address: company.address || '167, Ward No. 3, Khedawas, Thakhatgarh, Pali (Raj.)-306912',
              pan: company.pan || 'BNUPK1610E',
              gstin: company.gstin || '08BNUPK1610E1Z3',
              state: company.state || 'Rajasthan',
              state_code: sellerStateCode,
              place_of_supply: company.state || 'Rajasthan',
              contact_person: 'Rajesh Kumar',
              phone: company.phone || '+91-9460820878',
              email: company.email || 'saideepjewellers78@gmail.com'
            };
          }
          const cName = (data.customer?.name || '').trim();
          return {
            name: cName || 'Walk-in Customer',
            address: data.customer?.address || 'Takhatgarh, Pali (Raj.)',
            pan: data.customer?.pan || '',
            gstin: data.customer?.gstin || '',
            state: data.customer?.state || 'Rajasthan',
            state_code: buyerStateCode,
            place_of_supply: data.customer?.state || 'Rajasthan',
            contact_person: data.customer?.contact_person || '',
            phone: data.customer?.phone || '',
            email: data.customer?.email || ''
          };
        })(),
        """

text = text[:s_idx] + new_parties + text[b_end:]

with open('frontend/src/utils/invoicePdfUtils.ts', 'w', encoding='utf-8') as f:
    f.write(text)
print("invoicePdfUtils.ts successfully updated!")
