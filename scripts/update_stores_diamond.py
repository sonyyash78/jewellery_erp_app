import re

# 1. Update purchaseStore.ts
def update_purchase_store(path):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Update PurchaseItem metalType
    c = c.replace("metalType: 'Gold' | 'Silver';", "metalType: 'Gold' | 'Silver' | 'Diamond';\n  diamondType?: string;\n  shape?: string;\n  pieces?: number;\n  colour?: string;\n  clarity?: string;\n  certificateNo?: string;\n  weightGm?: number;\n  ratePerGm?: number;")
    
    # Update PurchaseStoreState
    if 'diamondForm:' not in c:
        old_state_def = """  silverForm: {
    itemName: string;
    grossWeight: number;
    stoneWeight: number;
    tanch: number;
    wastage: number;
    metalRate: number;
    makingChargeType?: string;
    makingChargeValue?: number;
    testingMeltingCharge: number;
    otherCharges: number;
    discount: number;
  };"""
        new_state_def = """  silverForm: {
    itemName: string;
    grossWeight: number;
    stoneWeight: number;
    tanch: number;
    wastage: number;
    metalRate: number;
    makingChargeType?: string;
    makingChargeValue?: number;
    testingMeltingCharge: number;
    otherCharges: number;
    discount: number;
  };
  diamondForm: {
    itemName: string;
    diamondType: string;
    shape: string;
    weightGm: number;
    pieces: number;
    ratePerGm: number;
    colour: string;
    clarity: string;
    certificateNo: string;
    labourCharge: number;
    otherCharges: number;
    discount: number;
  };"""
        c = c.replace(old_state_def, new_state_def)
        c = c.replace(
            "updateSilverForm: (key: string, value: any) => void;",
            "updateSilverForm: (key: string, value: any) => void;\n  updateDiamondForm: (key: string, value: any) => void;"
        )

    # Update create initial values
    if "diamondForm: {" not in c:
        old_init = """  silverForm: {
    itemName: '', grossWeight: 0, stoneWeight: 0, tanch: 99.9, wastage: 0,
    metalRate: 0, testingMeltingCharge: 0, makingChargeType: 'flat', makingChargeValue: 0, otherCharges: 0, discount: 0
  },"""
        new_init = """  silverForm: {
    itemName: '', grossWeight: 0, stoneWeight: 0, tanch: 99.9, wastage: 0,
    metalRate: 0, testingMeltingCharge: 0, makingChargeType: 'flat', makingChargeValue: 0, otherCharges: 0, discount: 0
  },
  diamondForm: {
    itemName: '', diamondType: 'NATURAL', shape: 'Round', weightGm: 0, pieces: 1, ratePerGm: 25000,
    colour: 'G', clarity: 'VS1', certificateNo: '', labourCharge: 0, otherCharges: 0, discount: 0
  },"""
        c = c.replace(old_init, new_init)
        c = c.replace(
            "updateSilverForm: (key, value) => set((state) => ({ silverForm: { ...state.silverForm, [key]: value } })),",
            "updateSilverForm: (key, value) => set((state) => ({ silverForm: { ...state.silverForm, [key]: value } })),\n  updateDiamondForm: (key, value) => set((state) => ({ diamondForm: { ...state.diamondForm, [key]: value } })),"
        )
        c = c.replace(
            "silverForm: { itemName: '', grossWeight: 0, stoneWeight: 0, tanch: 99.9, wastage: 0, metalRate: state.silverForm.metalRate, testingMeltingCharge: 0, makingChargeType: 'flat', makingChargeValue: 0, otherCharges: 0, discount: 0 },",
            "silverForm: { itemName: '', grossWeight: 0, stoneWeight: 0, tanch: 99.9, wastage: 0, metalRate: state.silverForm.metalRate, testingMeltingCharge: 0, makingChargeType: 'flat', makingChargeValue: 0, otherCharges: 0, discount: 0 },\n    diamondForm: { itemName: '', diamondType: 'NATURAL', shape: 'Round', weightGm: 0, pieces: 1, ratePerGm: 25000, colour: 'G', clarity: 'VS1', certificateNo: '', labourCharge: 0, otherCharges: 0, discount: 0 },"
        )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Updated {path}")

# 2. Update exchangeStore.ts
def update_exchange_store(path):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    c = c.replace("metal: 'Gold' | 'Silver';", "metal: 'Gold' | 'Silver' | 'Diamond';")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Updated {path}")

for p in [r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\store\purchaseStore.ts', r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\store\purchaseStore.ts']:
    update_purchase_store(p)

for p in [r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\store\exchangeStore.ts', r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\store\exchangeStore.ts']:
    update_exchange_store(p)
