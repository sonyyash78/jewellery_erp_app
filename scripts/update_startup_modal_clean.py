path = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\components\common\StartupCompanyModal.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("name: 'PRIDE GOLD'", "name: 'SAIDEEP JEWELLERS (GST)'")
text = text.replace("address: 'Sojati Gate, Jodhpur (Raj.)'", "address: '167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912'")
text = text.replace("invoice_prefix: 'PG'", "invoice_prefix: 'SJ'")
text = text.replace("{/* Company 2: Pride Gold (GST Tax Invoice) */}", "{/* Company 2: Saideep Jewellers (GST Tax Invoice) */}")
text = text.replace("{co2.address || 'Ghodo ka Chowk, Sojati Gate, Jodhpur'}", "{co2.address || '167, Ward No. 3, Khedawas, Takhatgarh, Pali'}")
text = text.replace("PG/S/1944/26-27", "SJ/S/1/26-27")
text = text.replace("Enter Pride Gold (GST)", "Enter Saideep Jewellers (GST)")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated StartupCompanyModal.tsx successfully!')
