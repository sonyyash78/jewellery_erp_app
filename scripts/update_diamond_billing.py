paths_billing = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\store\billingStore.ts',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\store\billingStore.ts'
]

for p in paths_billing:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # Update DiamondForm interface
    if 'weightGm:' not in c:
        c = c.replace(
            '  shape: string;\n  caratWeight: number;',
            '  shape: string;\n  weightGm: number;\n  caratWeight?: number;'
        )
    if 'ratePerGm:' not in c:
        c = c.replace(
            '  ratePerCarat: number;',
            '  ratePerGm: number;\n  ratePerCarat?: number;'
        )
    # Update initialDiamondForm
    if 'weightGm: 0,' not in c:
        c = c.replace(
            "  shape: 'Round',\n  caratWeight: 0,",
            "  shape: 'Round',\n  weightGm: 0,\n  caratWeight: 0,"
        )
    if 'ratePerGm: 25000,' not in c:
        c = c.replace(
            "  ratePerCarat: 50000,",
            "  ratePerGm: 25000,\n  ratePerCarat: 50000,"
        )
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)

print('Updated billingStore.ts')

paths_calc = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\MetalCalculator.tsx',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\pages\billing\MetalCalculator.tsx'
]

for p in paths_calc:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    # Replace calculation
    old_calc = """  // ─── Diamond calculations ───
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

    new_calc = """  // ─── Diamond calculations (Weight in Grams) ───
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

    c = c.replace(old_calc, new_calc)

    # Replace UI fields for Carat Weight & Rate
    old_fields = """            <div className="grid grid-cols-3 gap-2">
              <div>
                <InputLabel label="Carat Weight" />
                <input type="number" step="0.001" value={diamondForm.caratWeight ? diamondForm.caratWeight : ''}
                  onChange={e => updateDiamondForm('caratWeight', e.target.value === '' ? 0 : Number(e.target.value))}
                  placeholder="0.00" className="w-full bg-[#1A1A20] border border-cyan-800/60 rounded px-2 py-1 text-sm text-cyan-300 font-bold focus:border-cyan-400 outline-none font-mono" />
              </div>
              <div>
                <InputLabel label="Pieces" />
                <input type="number" value={diamondForm.pieces ? diamondForm.pieces : ''}
                  onChange={e => updateDiamondForm('pieces', e.target.value === '' ? 1 : Number(e.target.value))}
                  placeholder="1" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-cyan-500 outline-none font-mono" />
              </div>
              <div>
                <InputLabel label="Rate / Carat (₹)" />
                <input type="number" value={diamondForm.ratePerCarat ? diamondForm.ratePerCarat : ''}
                  onChange={e => updateDiamondForm('ratePerCarat', e.target.value === '' ? 0 : Number(e.target.value))}
                  placeholder="50000" className="w-full bg-[#1A1A20] border border-cyan-800/60 rounded px-2 py-1 text-sm text-cyan-300 font-bold focus:border-cyan-400 outline-none font-mono" />
              </div>
            </div>"""

    new_fields = """            <div className="grid grid-cols-3 gap-2">
              <div>
                <InputLabel label="Weight in Grams (gm)" />
                <input type="number" step="0.001" value={diamondForm.weightGm ?? (diamondForm.caratWeight ? diamondForm.caratWeight : '')}
                  onChange={e => {
                    const val = e.target.value === '' ? 0 : Number(e.target.value);
                    updateDiamondForm('weightGm', val);
                    updateDiamondForm('caratWeight', val);
                  }}
                  placeholder="0.000 gm" className="w-full bg-[#1A1A20] border border-cyan-800/60 rounded px-2 py-1 text-sm text-cyan-300 font-bold focus:border-cyan-400 outline-none font-mono" />
              </div>
              <div>
                <InputLabel label="Pieces" />
                <input type="number" value={diamondForm.pieces ? diamondForm.pieces : ''}
                  onChange={e => updateDiamondForm('pieces', e.target.value === '' ? 1 : Number(e.target.value))}
                  placeholder="1" className="w-full bg-[#1A1A20] border border-gray-700 rounded px-2 py-1 text-sm text-white focus:border-cyan-500 outline-none font-mono" />
              </div>
              <div>
                <InputLabel label="Rate / Gram (₹/gm)" />
                <input type="number" value={diamondForm.ratePerGm ?? (diamondForm.ratePerCarat ? diamondForm.ratePerCarat : '')}
                  onChange={e => {
                    const val = e.target.value === '' ? 0 : Number(e.target.value);
                    updateDiamondForm('ratePerGm', val);
                    updateDiamondForm('ratePerCarat', val);
                  }}
                  placeholder="25000" className="w-full bg-[#1A1A20] border border-cyan-800/60 rounded px-2 py-1 text-sm text-cyan-300 font-bold focus:border-cyan-400 outline-none font-mono" />
              </div>
            </div>"""

    c = c.replace(old_fields, new_fields)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)

print('Updated MetalCalculator.tsx')
