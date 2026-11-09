import os

path = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\invoicePdfUtils.ts'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update fallback city and jurisdiction to Takhatgarh / PALI
old_city_block = """      city: data.company?.city || settings.city || 'Jodhpur',

      state: data.company?.state || settings.state || 'Rajasthan',

      state_code: data.company?.state_code || settings.state_code || '08',

      jurisdiction_city: data.company?.jurisdiction_city || settings.jurisdiction_city || 'JODHPUR',"""

new_city_block = """      city: data.company?.city || settings.city || 'Takhatgarh',

      state: data.company?.state || settings.state || 'Rajasthan',

      state_code: data.company?.state_code || settings.state_code || '08',

      jurisdiction_city: data.company?.jurisdiction_city || settings.jurisdiction_city || 'PALI',"""

if old_city_block in text:
    text = text.replace(old_city_block, new_city_block, 1)
else:
    print('Notice: old_city_block pattern not matched directly, checking normalized...')
    # Try with single newlines
    old_city_block_single = old_city_block.replace('\n\n', '\n')
    new_city_block_single = new_city_block.replace('\n\n', '\n')
    text = text.replace(old_city_block_single, new_city_block_single, 1)

# 2. Update isGstCompany
old_is_gst = """    const isGstCompany = Boolean(
      company.gst_enabled === true ||
      data.company?.gst_enabled === true ||
      data.company?.id === 2 ||
      (data as any).company_id === 2 ||
      company.name?.toUpperCase().includes('PRIDE') ||
      String(data.invoice?.invoice_number || '').startsWith('PG/') ||
      String(data.invoice?.invoice_number || '').startsWith('SJ/S/')
    );
    const isPrideGold = isGstCompany;

    if (isPrideGold) {"""

new_is_gst = """    const isGstCompany = Boolean(
      company.gst_enabled === true ||
      data.company?.gst_enabled === true ||
      data.company?.id === 2 ||
      (data as any).company_id === 2 ||
      String(data.invoice?.invoice_number || '').startsWith('SJ/S/') ||
      String(data.invoice?.invoice_number || '').startsWith('PUR-') && company.gst_enabled === true
    );
    const isPrideGold = isGstCompany;

    if (isPrideGold) {"""

text = text.replace(old_is_gst, new_is_gst, 1)

# 3. Update seller and buyer inside isPrideGold
old_parties_start = text.find('        seller: (() => {')
old_parties_end = text.find('        items: gstItems,', old_parties_start)

if old_parties_start != -1 and old_parties_end != -1:
    new_parties_block = """        seller: {
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
          declaration: company.declaration || 'We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.',
          stamp_url: company.stamp_url,
          signature_url: company.signature_url
        },
        buyer: (() => {
          const isPurchase = (data as any).type === 'purchase' || String(data.invoice?.invoice_number || '').startsWith('PUR-');
          const party = (data as any).seller || (data as any).supplier || data.customer || {};
          const partyName = (party.name || party.first_name || (data as any).customer_name || '').trim();
          return {
            name: partyName || (isPurchase ? 'Supplier / Vendor' : 'Walk-in Customer'),
            address: party.address || (isPurchase ? '' : 'Takhatgarh, Pali (Raj.)'),
            pan: party.pan || party.aadhaar_pan || '',
            gstin: party.gstin || party.gst_number || '',
            state: party.state || 'Rajasthan',
            state_code: String(party.state_code || buyerStateCode || '08').padStart(2, '0'),
            place_of_supply: party.place_of_supply || party.state || 'Rajasthan',
            contact_person: party.contact_person || '',
            phone: party.phone || party.mobile || '',
            email: party.email || ''
          };
        })(),
"""
    text = text[:old_parties_start] + new_parties_block + text[old_parties_end:]
    print('Updated seller and buyer in invoicePdfUtils.ts!')
else:
    print('Could not find parties block in invoicePdfUtils.ts')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Successfully saved invoicePdfUtils.ts!')
