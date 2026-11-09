import os

p = r"c:\Users\YASH SONI\Desktop\jeweller-app\backend\app\schemas\invoice.py"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

is_crlf = "\r\n" in c
c_norm = c.replace("\r\n", "\n")

target1 = """class InvoiceItemCreate(BaseModel):
    inventory_item_id: Optional[int] = None
    stock_item_id: Optional[int] = None
    item_name: str
    item_type: ItemType
    final_price: float
    gold_calculation: Optional[GoldCalcCreate] = None
    silver_calculation: Optional[SilverCalcCreate] = None"""

replacement1 = """class DiamondCalcCreate(BaseModel):
    weight_gm: float = 0.0
    weight_carats: float = 0.0
    pieces: int = 1
    rate_per_gm: float = 0.0
    rate_per_carat: float = 0.0
    diamond_type: str = "NATURAL"
    diamond_form: str = "CUT_AND_POLISHED"
    shape: Optional[str] = None
    clarity: Optional[str] = None
    colour: Optional[str] = None
    certificate_no: Optional[str] = None
    discount: float = 0.0
    making_charges: float = 0.0
    other_charges: float = 0.0
    total_diamond_value: float = 0.0

class InvoiceItemCreate(BaseModel):
    inventory_item_id: Optional[int] = None
    stock_item_id: Optional[int] = None
    item_name: str
    item_type: ItemType
    final_price: float
    gold_calculation: Optional[GoldCalcCreate] = None
    silver_calculation: Optional[SilverCalcCreate] = None
    diamond_calculation: Optional[DiamondCalcCreate] = None"""

target2 = """class InvoiceCreate(BaseModel):
    customer_id: Optional[int] = None"""

replacement2 = """class InvoiceCreate(BaseModel):
    company_id: Optional[int] = 1
    customer_id: Optional[int] = None"""

target3 = """class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str"""

replacement3 = """class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    company_id: Optional[int] = 1"""

assert target1 in c_norm, "target1 not found"
assert target2 in c_norm, "target2 not found"
assert target3 in c_norm, "target3 not found"

c_norm = c_norm.replace(target1, replacement1, 1)
c_norm = c_norm.replace(target2, replacement2, 1)
c_norm = c_norm.replace(target3, replacement3, 1)

final_c = c_norm.replace("\n", "\r\n") if is_crlf else c_norm
with open(p, "w", encoding="utf-8") as f:
    f.write(final_c)

print("Updated backend/app/schemas/invoice.py successfully")
