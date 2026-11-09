path = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\gst_pdf_template.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = """    co_name = company.get("name", "SAIDEEP JEWELLERS")
    co_addr = company.get("address", "1st Floor, Near Koira Ji ka Bera, Ghodo ka Chowk, Sojati Gate, Jodhpur (Raj.)- 342001")
    co_gstin = company.get("gstin", "08AEZPK5007N1ZS")
    co_pan = company.get("pan", "AEZPK5007N")
    co_state = company.get("state", "Rajasthan")
    co_state_code = company.get("state_code", "08")
    co_phone = company.get("phone", "0291-2640999, +91-9929562800")
    co_email = company.get("email", "saideepjewellers78@gmail.com")
    co_jurisdiction = company.get("jurisdiction_city", "JODHPUR")
    co_declaration = company.get("declaration", "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.")

    buyer_name = buyer.get("name", buyer.get("first_name", "Saideep Jewellers"))
    if buyer.get("last_name"):
        buyer_name += f" {buyer['last_name']}"
    buyer_addr = buyer.get("address", "167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912")
    buyer_gstin = buyer.get("gstin", buyer.get("gst_number", "08BNUPK1610E1Z3"))
    buyer_pan = buyer.get("pan", buyer.get("aadhaar_pan", "BNUPK1610E"))
    buyer_state = buyer.get("state", "Rajasthan")
    buyer_state_code = buyer.get("state_code", "08")
    place_of_supply = buyer.get("place_of_supply", "Rajasthan")
    buyer_contact_person = buyer.get("contact_person", "Rajesh Kumar")
    buyer_phone = buyer.get("phone", "+91-9460820878")
    buyer_email = buyer.get("email", "saideepjewellers78@gmail.com")"""

new_block = """    co_name = company.get("name", "SAIDEEP JEWELLERS")
    co_addr = company.get("address", "167, Ward No. 3, Khedawas, Takhatgarh, Pali (Raj.)-306912")
    co_gstin = company.get("gstin", "08BNUPK1610E1Z3")
    co_pan = company.get("pan", "BNUPK1610E")
    co_state = company.get("state", "Rajasthan")
    co_state_code = company.get("state_code", "08")
    co_phone = company.get("phone", "+91-9460820878")
    co_email = company.get("email", "saideepjewellers78@gmail.com")
    co_jurisdiction = company.get("jurisdiction_city", "PALI")
    co_declaration = company.get("declaration", "We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.")

    buyer_name = (buyer.get("name") or buyer.get("first_name") or "Walk-in Customer").strip()
    if buyer.get("last_name"):
        buyer_name += f" {buyer['last_name']}"
    buyer_addr = buyer.get("address", "")
    buyer_gstin = buyer.get("gstin") or buyer.get("gst_number") or ""
    buyer_pan = buyer.get("pan") or buyer.get("aadhaar_pan") or ""
    buyer_state = buyer.get("state", "Rajasthan")
    buyer_state_code = buyer.get("state_code", "08")
    place_of_supply = buyer.get("place_of_supply") or buyer_state
    buyer_contact_person = buyer.get("contact_person", "")
    buyer_phone = buyer.get("phone") or buyer.get("mobile") or ""
    buyer_email = buyer.get("email", "")"""

assert old_block in text, "old_block not found in gst_pdf_template.py"
text = text.replace(old_block, new_block, 1)

# Also check Stamp city and JURISDICTION text in template
text = text.replace('SUBJECT TO JODHPUR JURISDICTION', 'SUBJECT TO PALI JURISDICTION')
text = text.replace('SUBJECT TO {co_jurisdiction} JURISDICTION', 'SUBJECT TO {co_jurisdiction or "PALI"} JURISDICTION')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated gst_pdf_template.py successfully!')
