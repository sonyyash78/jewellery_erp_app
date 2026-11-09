import os
import re

# 1. Update ReportViewer.tsx
p_rep = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\reports\ReportViewer.tsx"
with open(p_rep, "r", encoding="utf-8") as f:
    rep_c = f.read()

if "useCompanyStore" not in rep_c:
    rep_c = "import { useCompanyStore } from '../../store/companyStore';\n" + rep_c
    rep_c = rep_c.replace(
        "export default function ReportViewer({ reportType }: { reportType: string }) {",
        "export default function ReportViewer({ reportType }: { reportType: string }) {\n  const { currentCompanyId, currentCompany } = useCompanyStore();"
    )
    rep_c = rep_c.replace(
        "useEffect(() => {\n    if (timeFilter !== 'Custom') {\n      fetchReport();\n    }\n  }, [reportType, timeFilter]);",
        "useEffect(() => {\n    if (timeFilter !== 'Custom') {\n      fetchReport();\n    }\n  }, [reportType, timeFilter, currentCompanyId]);"
    )
    rep_c = rep_c.replace(
        "const params = new URLSearchParams();",
        "const params = new URLSearchParams();\n      params.append('company_id', String(currentCompanyId || 1));"
    )
    # Add company badge above report title
    old_badge_target = '<h2 className="text-xl font-bold text-primary uppercase tracking-widest">{reportType} Report</h2>'
    new_badge_target = """<div className="flex items-center gap-2 mb-1.5">
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider border ${
              currentCompany?.gst_enabled
                ? 'bg-cyan-500/15 border-cyan-500/30 text-cyan-400'
                : 'bg-amber-500/15 border-amber-500/30 text-amber-300'
            }`}>
              {currentCompany?.name || 'Saideep Jewellers'} {currentCompany?.gst_enabled ? '• GST Tax Analytics' : '• Normal Retail Analytics'}
            </span>
          </div>
          <h2 className="text-xl font-bold text-primary uppercase tracking-widest">{reportType} Report</h2>"""
    rep_c = rep_c.replace(old_badge_target, new_badge_target)
    with open(p_rep, "w", encoding="utf-8") as f:
        f.write(rep_c)
    print("Updated ReportViewer.tsx with company isolation and visual badges")

# 2. Update invoicePdfUtils.ts
p_pdf = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\invoicePdfUtils.ts"
with open(p_pdf, "r", encoding="utf-8") as f:
    pdf_c = f.read()

# Make sure data.company takes precedence over settings
old_company_obj = """    const company = { 
      name: settings.business_name || settings.store_name || settings.name || data.company?.name || defaultStoreName, 
      address: settings.address || settings.store_address || data.company?.address || '', 
      phone: settings.phone || settings.store_phone || data.company?.phone || '', 
      email: settings.email || settings.store_email || data.company?.email || '', 
      gstin: settings.gstin || settings.store_gstin || data.company?.gstin || '',
      tagline: settings.tagline || data.company?.tagline || 'TIMELESS BEAUTY. TRUSTED FOREVER.',
      ...settings
    };"""

new_company_obj = """    const company = { 
      ...settings,
      name: data.company?.name || settings.business_name || settings.store_name || settings.name || defaultStoreName, 
      address: data.company?.address || settings.address || settings.store_address || '', 
      phone: data.company?.phone || settings.phone || settings.store_phone || '', 
      email: data.company?.email || settings.email || settings.store_email || '', 
      gstin: data.company?.gstin || settings.gstin || settings.store_gstin || '',
      pan: data.company?.pan || settings.pan || '',
      city: data.company?.city || settings.city || 'Jodhpur',
      state: data.company?.state || settings.state || 'Rajasthan',
      state_code: data.company?.state_code || settings.state_code || '08',
      jurisdiction_city: data.company?.jurisdiction_city || settings.jurisdiction_city || 'JODHPUR',
      declaration: data.company?.declaration || settings.declaration || '',
      tagline: settings.tagline || data.company?.tagline || 'TIMELESS BEAUTY. TRUSTED FOREVER.'
    };"""

if old_company_obj in pdf_c:
    pdf_c = pdf_c.replace(old_company_obj, new_company_obj)
    print("Updated company precedence in invoicePdfUtils.ts")

# Make sure buyer name for Pride Gold bills is Saideep Jewellers
old_buyer_block = """        buyer: {
          name: data.customer?.name || 'Saideep Jewellers',
          address: data.customer?.address || (data.customer?.name?.toLowerCase().includes('saideep') || !data.customer?.name ? '167, Ward No. 3, Khedawas, Thakhatgarh,Pali (Raj.)-306912' : 'Takhatgarh, Pali (Raj.)'),
          pan: data.customer?.pan || (data.customer?.name?.toLowerCase().includes('saideep') || !data.customer?.name ? 'BNUPK1610E' : ''),
          gstin: data.customer?.gstin || (data.customer?.name?.toLowerCase().includes('saideep') || !data.customer?.name ? '08BNUPK1610E1Z3' : ''),
          state: data.customer?.state || 'Rajasthan',
          state_code: buyerStateCode,
          place_of_supply: data.customer?.state || 'Rajasthan',
          contact_person: 'Rajesh Kumar',
          phone: data.customer?.phone || '+91-9460820878',
          email: data.customer?.email || 'saideepjewellers78@gmail.com'
        },"""

new_buyer_block = """        buyer: (() => {
          const rawName = data.customer?.name || '';
          const isSaideep = !rawName ||
            rawName.toLowerCase().includes('saideep') ||
            rawName.toLowerCase().includes('yash') ||
            data.customer?.pan === 'BNUPK1610E' ||
            data.customer?.gstin === '08BNUPK1610E1Z3';

          return {
            name: isSaideep ? 'Saideep Jewellers' : rawName,
            address: data.customer?.address || (isSaideep ? '167, Ward No. 3, Khedawas, Thakhatgarh,Pali (Raj.)-306912' : 'Takhatgarh, Pali (Raj.)'),
            pan: data.customer?.pan || (isSaideep ? 'BNUPK1610E' : ''),
            gstin: data.customer?.gstin || (isSaideep ? '08BNUPK1610E1Z3' : ''),
            state: data.customer?.state || 'Rajasthan',
            state_code: buyerStateCode,
            place_of_supply: data.customer?.state || 'Rajasthan',
            contact_person: isSaideep ? 'Rajesh Kumar' : (data.customer?.contact_person || rawName),
            phone: data.customer?.phone || (isSaideep ? '+91-9460820878' : ''),
            email: data.customer?.email || (isSaideep ? 'saideepjewellers78@gmail.com' : '')
          };
        })(),"""

if old_buyer_block in pdf_c:
    pdf_c = pdf_c.replace(old_buyer_block, new_buyer_block)
    print("Updated buyer mapping in invoicePdfUtils.ts")

with open(p_pdf, "w", encoding="utf-8") as f:
    f.write(pdf_c)

print("invoicePdfUtils.ts updated successfully")
