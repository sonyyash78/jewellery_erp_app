with open('frontend/src/utils/invoicePdfUtils.ts', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace isPrideGold condition
old_cond = """    // --- MULTI-COMPANY TEMPLATE RESOLUTION ---
    // If company has GST enabled (Company 2 - Pride Gold), render the GST Tax Invoice layout.
    // If Company 1 (Saideep, gst_enabled = false), it continues down to the legacy template UNTOUCHED.
    const isPrideGold = Boolean(
      company.gst_enabled ||
      data.company?.gst_enabled ||
      company.name?.toUpperCase().includes('PRIDE') ||
      String(data.invoice?.invoice_number || '').startsWith('PG/')
    );"""

new_cond = """    // --- MULTI-COMPANY TEMPLATE RESOLUTION ---
    // Resolve Company from data.company, or active company store if running in app
    let currentCoGst = false;
    let currentCoId = 1;
    try {
      const { useCompanyStore } = await import('../store/companyStore');
      const activeCo = useCompanyStore.getState().currentCompany;
      if (activeCo) {
        currentCoGst = Boolean(activeCo.gst_enabled);
        currentCoId = Number(activeCo.id);
      }
    } catch {}

    const isGstCompany = Boolean(
      company.gst_enabled === true ||
      data.company?.gst_enabled === true ||
      data.company?.id === 2 ||
      (data as any).company_id === 2 ||
      (currentCoGst && currentCoId === 2) ||
      company.name?.toUpperCase().includes('PRIDE') ||
      String(data.invoice?.invoice_number || '').startsWith('PG/') ||
      String(data.invoice?.invoice_number || '').startsWith('SJ/S/')
    );
    const isPrideGold = isGstCompany;"""

assert old_cond in c, "old_cond not found in invoicePdfUtils.ts"
c = c.replace(old_cond, new_cond, 1)

# Now check seller and buyer generation inside if (isPrideGold)
old_parties = """        seller: {
          name: company.name || 'SAIDEEP JEWELLERS',
          address: company.address || '167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912',
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
        },
        buyer: (() => {
          const cName = (data.customer?.name || '').trim();
          const isSaideep = !cName || cName.toLowerCase().includes('saideep') || cName.toLowerCase().includes('yash') || data.customer?.gstin === '08BNUPK1610E1Z3';
          return {
            name: isSaideep ? 'Saideep Jewellers' : cName,
            address: isSaideep ? '167, Ward No. 3, Khedawas, Thakhatgarh, Pali (Raj.)-306912' : (data.customer?.address || 'Takhatgarh, Pali (Raj.)'),
            pan: isSaideep ? 'BNUPK1610E' : (data.customer?.pan || ''),
            gstin: isSaideep ? '08BNUPK1610E1Z3' : (data.customer?.gstin || ''),
            state: data.customer?.state || 'Rajasthan',
            state_code: buyerStateCode,
            place_of_supply: data.customer?.state || 'Rajasthan',
            contact_person: isSaideep ? 'Rajesh Kumar' : (data.customer?.contact_person || ''),
            phone: isSaideep ? '+91-9460820878' : (data.customer?.phone || ''),
            email: isSaideep ? 'saideepjewellers78@gmail.com' : (data.customer?.email || '')
          };
        })(),"""

new_parties = """        seller: (() => {
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
        })(),"""

assert old_parties in c, "old_parties not found in invoicePdfUtils.ts"
c = c.replace(old_parties, new_parties, 1)

with open('frontend/src/utils/invoicePdfUtils.ts', 'w', encoding='utf-8') as f:
    f.write(c)
print("Updated invoicePdfUtils.ts successfully!")
