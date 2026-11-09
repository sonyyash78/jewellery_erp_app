import os
import re

repo_root = r"C:\Users\YASH SONI\Desktop\jeweller-app"

# 1. Update frontend/src/utils/invoicePdfUtils.ts
pdf_utils_path = os.path.join(repo_root, "frontend", "src", "utils", "invoicePdfUtils.ts")
with open(pdf_utils_path, "r", encoding="utf-8") as f:
    pdf_utils_code = f.read()

# Replace Pride Gold fallbacks with Saideep Jewellers
pdf_utils_code = pdf_utils_code.replace("name: company.name || 'PRIDE GOLD',", "name: company.name || 'SAIDEEP JEWELLERS',")
pdf_utils_code = pdf_utils_code.replace("address: company.address || '1st Floor, Near Koira Ji ka Bera, Ghodo ka Chowk, Sojati Gate, Jodhpur (Raj.)- 342001',",
                                        "address: company.address || '167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912',")
pdf_utils_code = pdf_utils_code.replace("gstin: company.gstin || '08AEZPK5007N1ZS',", "gstin: company.gstin || '08BNUPK1610E1Z3',")
pdf_utils_code = pdf_utils_code.replace("pan: company.pan || 'AEZPK5007N',", "pan: company.pan || 'BNUPK1610E',")
pdf_utils_code = pdf_utils_code.replace("phone: company.phone || '0291-2640999,+91-9929562800',", "phone: company.phone || '+91-9460820878',")
pdf_utils_code = pdf_utils_code.replace("email: company.email || 'info.pridegoldjdr@gmail.com',", "email: company.email || 'saideepjewellers78@gmail.com',")
pdf_utils_code = pdf_utils_code.replace("jurisdiction_city: company.jurisdiction_city || 'JODHPUR',", "jurisdiction_city: company.jurisdiction_city || 'PALI',")

# Remove isSaideep buyer override
old_buyer_fn = """        buyer: (() => {
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

new_buyer_fn = """        buyer: (() => {
          const cName = (data.customer?.name || '').trim();
          return {
            name: cName || 'Walk-in Customer',
            address: data.customer?.address || '',
            pan: data.customer?.pan || '',
            gstin: data.customer?.gstin || '',
            state: data.customer?.state || 'Rajasthan',
            state_code: buyerStateCode,
            place_of_supply: data.customer?.place_of_supply || data.customer?.state || 'Rajasthan',
            contact_person: data.customer?.contact_person || cName,
            phone: data.customer?.phone || '',
            email: data.customer?.email || ''
          };
        })(),"""

if old_buyer_fn in pdf_utils_code:
    pdf_utils_code = pdf_utils_code.replace(old_buyer_fn, new_buyer_fn)
    print("Updated buyer resolver in invoicePdfUtils.ts")

with open(pdf_utils_path, "w", encoding="utf-8") as f:
    f.write(pdf_utils_code)

# 2. Update frontend/src/utils/gstInvoiceHtml.ts
gst_html_path = os.path.join(repo_root, "frontend", "src", "utils", "gstInvoiceHtml.ts")
with open(gst_html_path, "r", encoding="utf-8") as f:
    gst_html_code = f.read()

# Dynamic stamp circle with seller name
gst_html_code = gst_html_code.replace("<div>● PRIDE GOLD ●</div>", "<div>● ${seller.name} ●</div>")
# Remove hardcoded 342001 Jodhpur pincode from address fallback
gst_html_code = gst_html_code.replace("${(seller.address?.includes('India') || seller.address?.includes('342001, India')) ? '' : `<div>${seller.state || 'Rajasthan'} - 342001, India</div>`}",
                                      "${seller.address?.includes('India') ? '' : `<div>${seller.state || 'Rajasthan'}, India</div>`}")

with open(gst_html_path, "w", encoding="utf-8") as f:
    f.write(gst_html_code)
print("Updated stamp circle and address in gstInvoiceHtml.ts")

# 3. Update frontend/src/components/common/CompanySelector.tsx
selector_path = os.path.join(repo_root, "frontend", "src", "components", "common", "CompanySelector.tsx")
with open(selector_path, "r", encoding="utf-8") as f:
    sel_code = f.read()

# Make badges distinct: Normal (No-GST) vs GST Tax Invoice
old_badge = """            {currentCompany?.gst_enabled ? (
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-1 py-0.2 rounded font-bold">
                GST
              </span>
            ) : (
              <span className="text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30 px-1 py-0.2 rounded font-bold">
                C1
              </span>
            )}"""

new_badge = """            {currentCompany?.gst_enabled ? (
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-1.5 py-0.5 rounded font-bold">
                GST Tax Invoice
              </span>
            ) : (
              <span className="text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30 px-1.5 py-0.5 rounded font-bold">
                Normal (No-GST)
              </span>
            )}"""

if old_badge in sel_code:
    sel_code = sel_code.replace(old_badge, new_badge)
    print("Updated badges in CompanySelector.tsx")
    with open(selector_path, "w", encoding="utf-8") as f:
        f.write(sel_code)

print("Frontend helper utilities updated successfully!")
