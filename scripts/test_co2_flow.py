import requests

res = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json={'username': 'admin', 'password': 'admin'})
token = res.json().get('access_token')
headers = {'Authorization': f'Bearer {token}', 'X-Company-ID': '2'}

payload = {
    'company_id': 2,
    'customer_id': 1,
    'subtotal': 389320.0,
    'tax_amount': 11679.6,
    'discount_amount': 0.0,
    'grand_total': 401000.0,
    'amount_paid': 401000.0,
    'status': 'Paid',
    'bill_type': 'Cash',
    'items': [
        {
            'item_name': 'SILVER BAR',
            'item_type': 'SILVER',
            'final_price': 401000.0,
            'silver_calculation': {
                'applied_rate': 194660.0,
                'gross_weight': 2000.0,
                'stone_weight': 0.0,
                'net_weight': 2000.0,
                'tanch': 100.0,
                'wastage': 0.0,
                'fine_weight': 2000.0,
                'making_charge_type': 'flat',
                'making_charge_rate': 0.0,
                'making_charges_amount': 0.0,
                'testing_melting_charges': 0.0,
                'other_charges': 0.0
            }
        }
    ]
}

res_create = requests.post('http://127.0.0.1:8000/api/v1/invoices/', json=payload, headers=headers)
print('Create Co2 Invoice status:', res_create.status_code)
created_inv = res_create.json()
print('Created Invoice No:', created_inv.get('invoice_number'))
print('Company ID on invoice:', created_inv.get('company_id'))

inv_id = created_inv.get('id')

# Verify Company 2 list has 1 invoice
res_inv2 = requests.get('http://127.0.0.1:8000/api/v1/invoices/', headers=headers)
print('Invoices in Company 2:', len(res_inv2.json()))

# Verify Company 1 list STILL has 7 invoices (zero data bleed!)
headers['X-Company-ID'] = '1'
res_inv1 = requests.get('http://127.0.0.1:8000/api/v1/invoices/', headers=headers)
print('Invoices in Company 1:', len(res_inv1.json()))

# Fetch PDF Data for the new Pride Gold invoice
pdf_res = requests.get(f'http://127.0.0.1:8000/api/v1/invoices/{inv_id}/pdf-data', headers={'Authorization': f'Bearer {token}'})
pdf_data = pdf_res.json()
print('Seller Name:', pdf_data['company']['name'])
print('Seller GSTIN:', pdf_data['company']['gstin'])
print('Buyer Name:', pdf_data['customer']['name'])
print('Buyer GSTIN:', pdf_data['customer']['gstin'])
print('Buyer PAN:', pdf_data['customer']['pan'])
