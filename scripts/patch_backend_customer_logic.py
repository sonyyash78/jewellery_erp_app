import re

customers_path = r'c:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\customers.py'
with open(customers_path, 'r', encoding='utf-8') as f:
    cust_code = f.read()

pattern = r'if existing:\s+raise HTTPException\(\s+status_code=400,\s+detail="A customer with this mobile number already exists in your store\.",\s+\)'

replacement = '''if existing:
        # Seamlessly update existing customer data rather than throwing an error
        update_data = customer_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None and value != '':
                setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing'''

new_code, count = re.subn(pattern, replacement, cust_code)
if count > 0:
    with open(customers_path, 'w', encoding='utf-8') as f:
        f.write(new_code)
    print(f"Updated customers.py successfully! (replaces={count})")
else:
    print("Pattern not matched in customers.py")
