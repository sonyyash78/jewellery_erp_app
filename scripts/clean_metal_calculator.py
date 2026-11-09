paths = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\MetalCalculator.tsx',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\pages\billing\MetalCalculator.tsx'
]

for p in paths:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    # Fix lines 105-140
    old_calc = """  // ── Diamond calculations ──
  const dCaratWeight = Math.max(0, diamondForm.caratWeight || 0);
  const dRate = Math.max(0, diamondForm.ratePerCarat || 0);
  const dSubtotal = dCaratWeight * dRate;
  const dMaking = Math.max(0, diamondForm.makingCharges || 0);
  const dOther = Math.max(0, diamondForm.otherCharges || 0);
  const dDiscount = Math.max(0, diamondForm.discount || 0);
  const dTaxable = Math.max(0, dSubtotal + dMaking + dOther - dDiscount);

  const handleDiamondAdd = () => {
    if (dCaratWeight <= 0) { toast.error('Carat weight must be > 0'); return; }
    if (dRate <= 0) { toast.error('Rate per carat must be > 0'); return; }
    const item: BillItem = {
      id: editingItemId || Math.random().toString(36).substring(7),
      itemType: 'Diamond',
      itemName: diamondForm.itemName.trim() || `${diamondForm.diamondType} ${diamondForm.shape} Diamond`,
      purityDisplay: `${diamondForm.colour}/${diamondForm.clarity}`,
      touchDisplay: 100,
      wastageDisplay: 0,
      grossWeight: dCaratWeight,
      stoneWeight: 0,
      netWeight: dCaratWeight,
      fineWeight: dCaratWeight,
      rateDisplay: dRate,
      metalValue: dSubtotal,
      makingAmount: dMaking,
      hallmark: 0,
      otherCharges: dOther,
      discount: dDiscount,
      taxableAmount: dTaxable,
      rawDiamond: { ...diamondForm }
    };
    addToCart(item);
    toast.success(editingItemId ? 'Item Updated in Bill' : 'Added to Bill');
    resetDiamondForm();
  };"""

    new_calc = """  // ── Diamond calculations (Weight in Grams) ──
  const dWeightGm = Math.max(0, diamondForm.weightGm ?? (diamondForm.caratWeight || 0));
  const dRate = Math.max(0, diamondForm.ratePerGm ?? (diamondForm.ratePerCarat || 0));
  const dSubtotal = dWeightGm * dRate;
  const dMaking = Math.max(0, diamondForm.makingCharges || 0);
  const dOther = Math.max(0, diamondForm.otherCharges || 0);
  const dDiscount = Math.max(0, diamondForm.discount || 0);
  const dTaxable = Math.max(0, dSubtotal + dMaking + dOther - dDiscount);

  const handleDiamondAdd = () => {
    if (dWeightGm <= 0) { toast.error('Diamond weight in grams must be > 0'); return; }
    if (dRate <= 0) { toast.error('Rate per gram must be > 0'); return; }
    const item: BillItem = {
      id: editingItemId || Math.random().toString(36).substring(7),
      itemType: 'Diamond',
      itemName: diamondForm.itemName.trim() || `${diamondForm.diamondType} ${diamondForm.shape} Diamond`,
      purityDisplay: `${diamondForm.colour}/${diamondForm.clarity}`,
      touchDisplay: 100,
      wastageDisplay: 0,
      grossWeight: dWeightGm,
      stoneWeight: 0,
      netWeight: dWeightGm,
      fineWeight: dWeightGm,
      rateDisplay: dRate,
      metalValue: dSubtotal,
      makingAmount: dMaking,
      hallmark: 0,
      otherCharges: dOther,
      discount: dDiscount,
      taxableAmount: dTaxable,
      rawDiamond: { ...diamondForm, weightGm: dWeightGm, ratePerGm: dRate }
    };
    addToCart(item);
    toast.success(editingItemId ? 'Item Updated in Bill' : 'Added to Bill');
    resetDiamondForm();
  };"""

    if old_calc in c:
        c = c.replace(old_calc, new_calc)

    # Remove duplicated diamond block from editing banner
    # In the editing banner, it should just be:
    # {isDiamond ? (diamondForm.itemName || `${diamondForm.diamondType} Diamond`) : isGold ? (goldForm.itemName || `${goldForm.purity} Gold`) : (silverForm.itemName || `${silverForm.silverPurity} Silver`)}
    # Find start and end of duplicated block
    banner_start = '<div className="text-[11px] text-gray-300">'
    banner_gold = '{isGold ? (goldForm.itemName || `${goldForm.purity} Gold`) : (silverForm.itemName || `${silverForm.silverPurity} Silver`)}'
    
    idx_start = c.find(banner_start)
    if idx_start != -1:
        idx_gold = c.find(banner_gold, idx_start)
        if idx_gold != -1 and idx_gold - idx_start > len(banner_start) + 20:
            # There is junk in between
            c = c[:idx_start + len(banner_start)] + '\n                {isDiamond ? (diamondForm.itemName || `${diamondForm.diamondType} Diamond`) : isGold ? (goldForm.itemName || `${goldForm.purity} Gold`) : (silverForm.itemName || `${silverForm.silverPurity} Silver`)}\n' + c[idx_gold + len(banner_gold):]

    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)

print('Cleaned up MetalCalculator.tsx')
