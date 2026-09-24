import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity } from 'react-native';

export interface ItemPayload {
  metalType: 'Gold' | 'Silver';
  itemName: string;
  category: string;
  grossWeight: number;
  stoneWeight: number;
  netWeight: number;
  touchPurity: number;
  wastage: number;
  fineWeight: number;
  metalRate: number;
  metalValue: number;
  makingChargeType: 'percent' | 'per_gm' | 'flat';
  makingChargeValue: number;
  makingAmount: number;
  hallmarkCharge: number;
  otherCharges: number;
  discount: number;
  taxableAmount: number;
}

interface Props {
  onAdd: (item: ItemPayload) => void;
  buttonLabel?: string;
  liveRates?: { gold14k: number, gold18k: number, gold22k: number, gold24k: number, silver: number };
  initialItem?: ItemPayload | null;
  onCancelEdit?: () => void;
}

export default function MobileMetalCalculator({ onAdd, buttonLabel = "ADD ITEM", liveRates, initialItem, onCancelEdit }: Props) {
  const [metal, setMetal] = useState<'Gold' | 'Silver'>('Gold');
  const [itemName, setItemName] = useState('');
  
  // Gold State
  const [gCategory, setGCategory] = useState('22K');
  const [gGross, setGGross] = useState('');
  const [gStone, setGStone] = useState('');
  const [gTouch, setGTouch] = useState('91.6');
  const [gWastage, setGWastage] = useState('0');
  const [gRate, setGRate] = useState(liveRates?.gold22k?.toString() || '72500');
  
  const [gMakingType, setGMakingType] = useState<'percent'|'per_gm'|'flat'>('flat');
  const [gMakingValue, setGMakingValue] = useState('0');
  const [gHallmark, setGHallmark] = useState('0');
  const [gOther, setGOther] = useState('0');
  const [gDiscount, setGDiscount] = useState('0');

  // Silver State
  const [sCategory, setSCategory] = useState('Fine');
  const [sGross, setSGross] = useState('');
  const [sStone, setSStone] = useState('');
  const [sTouch, setSTouch] = useState('99.9');
  const [sWastage, setSWastage] = useState('0');
  const [sRate, setSRate] = useState(liveRates?.silver?.toString() || '90000');
  
  const [sMakingType, setSMakingType] = useState<'percent'|'per_gm'|'flat'>('flat');
  const [sMakingValue, setSMakingValue] = useState('0');
  const [sHallmark, setSHallmark] = useState('0');
  const [sOther, setSOther] = useState('0');
  const [sDiscount, setSDiscount] = useState('0');

  // Watch initialItem to load into calculator for editing
  useEffect(() => {
    if (initialItem) {
      setMetal(initialItem.metalType);
      setItemName(initialItem.itemName || '');
      if (initialItem.metalType === 'Gold') {
        setGCategory(initialItem.category || '22K');
        setGGross(String(initialItem.grossWeight || ''));
        setGStone(String(initialItem.stoneWeight || ''));
        setGTouch(String(initialItem.touchPurity || '91.6'));
        setGWastage(String(initialItem.wastage || '0'));
        setGRate(String(initialItem.metalRate || '72500'));
        setGMakingType(initialItem.makingChargeType || 'flat');
        setGMakingValue(String(initialItem.makingChargeValue || '0'));
        setGHallmark(String(initialItem.hallmarkCharge || '0'));
        setGOther(String(initialItem.otherCharges || '0'));
        setGDiscount(String(initialItem.discount || '0'));
      } else {
        setSCategory(initialItem.category || 'Fine');
        setSGross(String(initialItem.grossWeight || ''));
        setSStone(String(initialItem.stoneWeight || ''));
        setSTouch(String(initialItem.touchPurity || '99.9'));
        setSWastage(String(initialItem.wastage || '0'));
        setSRate(String(initialItem.metalRate || '90000'));
        setSMakingType(initialItem.makingChargeType || 'flat');
        setSMakingValue(String(initialItem.makingChargeValue || '0'));
        setSHallmark(String(initialItem.hallmarkCharge || '0'));
        setSOther(String(initialItem.otherCharges || '0'));
        setSDiscount(String(initialItem.discount || '0'));
      }
    }
  }, [initialItem]);

  // Calculations
  const calculateGold = () => {
    const gross = parseFloat(gGross) || 0;
    const stone = parseFloat(gStone) || 0;
    const net = Math.max(0, gross - stone);
    const touch = parseFloat(gTouch) || 0;
    const waste = parseFloat(gWastage) || 0;
    const fine = net * ((touch + waste) / 100);
    const rate = parseFloat(gRate) || 0;
    const metalVal = fine * (rate / 10);
    
    let makingTotal = 0;
    const mVal = parseFloat(gMakingValue) || 0;
    if (gMakingType === 'percent') makingTotal = metalVal * (mVal / 100);
    else if (gMakingType === 'per_gm') makingTotal = net * mVal;
    else makingTotal = mVal;
    
    const hm = parseFloat(gHallmark) || 0;
    const oc = parseFloat(gOther) || 0;
    const disc = parseFloat(gDiscount) || 0;
    
    const taxAmt = metalVal + makingTotal + hm + oc - disc;
    return { net, fine, metalVal, makingTotal, taxAmt };
  };

  const calculateSilver = () => {
    const gross = parseFloat(sGross) || 0;
    const stone = parseFloat(sStone) || 0;
    const net = Math.max(0, gross - stone);
    const touch = parseFloat(sTouch) || 0;
    const waste = parseFloat(sWastage) || 0;
    const fine = net * ((touch + waste) / 100);
    const rate = parseFloat(sRate) || 0;
    const metalVal = fine * (rate / 1000);
    
    let makingTotal = 0;
    const mVal = parseFloat(sMakingValue) || 0;
    if (sMakingType === 'percent') makingTotal = metalVal * (mVal / 100);
    else if (sMakingType === 'per_gm') makingTotal = net * mVal;
    else makingTotal = mVal;
    
    const hm = parseFloat(sHallmark) || 0;
    const oc = parseFloat(sOther) || 0;
    const disc = parseFloat(sDiscount) || 0;
    
    const taxAmt = metalVal + makingTotal + hm + oc - disc;
    return { net, fine, metalVal, makingTotal, taxAmt };
  };

  const c = metal === 'Gold' ? calculateGold() : calculateSilver();

  const handleAdd = () => {
    if (metal === 'Gold') {
      onAdd({
        metalType: 'Gold',
        itemName: itemName || 'Gold Item',
        category: gCategory,
        grossWeight: parseFloat(gGross) || 0,
        stoneWeight: parseFloat(gStone) || 0,
        netWeight: c.net,
        touchPurity: parseFloat(gTouch) || 0,
        wastage: parseFloat(gWastage) || 0,
        fineWeight: c.fine,
        metalRate: parseFloat(gRate) || 0,
        metalValue: c.metalVal,
        makingChargeType: gMakingType,
        makingChargeValue: parseFloat(gMakingValue) || 0,
        makingAmount: c.makingTotal,
        hallmarkCharge: parseFloat(gHallmark) || 0,
        otherCharges: parseFloat(gOther) || 0,
        discount: parseFloat(gDiscount) || 0,
        taxableAmount: c.taxAmt
      });
      // Reset
      setGGross(''); setGStone(''); setGMakingValue('0'); setGHallmark('0'); setGOther('0'); setGDiscount('0');
    } else {
      onAdd({
        metalType: 'Silver',
        itemName: itemName || 'Silver Item',
        category: sCategory,
        grossWeight: parseFloat(sGross) || 0,
        stoneWeight: parseFloat(sStone) || 0,
        netWeight: c.net,
        touchPurity: parseFloat(sTouch) || 0,
        wastage: parseFloat(sWastage) || 0,
        fineWeight: c.fine,
        metalRate: parseFloat(sRate) || 0,
        metalValue: c.metalVal,
        makingChargeType: sMakingType,
        makingChargeValue: parseFloat(sMakingValue) || 0,
        makingAmount: c.makingTotal,
        hallmarkCharge: parseFloat(sHallmark) || 0,
        otherCharges: parseFloat(sOther) || 0,
        discount: parseFloat(sDiscount) || 0,
        taxableAmount: c.taxAmt
      });
      // Reset
      setSGross(''); setSStone(''); setSMakingValue('0'); setSHallmark('0'); setSOther('0'); setSDiscount('0');
    }
    setItemName('');
  };

  const renderSilverPurity = () => {
    const opts = [
      { l: 'Fine', t: '99.9', r: liveRates?.silver || 90000 },
      { l: 'Sterling', t: '92.5', r: (liveRates?.silver || 90000) * 0.925 },
      { l: 'Custom', t: '65.0', r: (liveRates?.silver || 90000) * 0.65 },
    ];
    return (
      <View style={styles.purityRow}>
        {opts.map(o => (
          <TouchableOpacity 
            key={o.l} 
            style={[styles.purityBtn, sCategory === o.l && styles.purityBtnActiveSilver]}
            onPress={() => { setSCategory(o.l); setSTouch(o.t); setSRate(o.r.toString()); }}
          >
            <Text style={[styles.purityText, sCategory === o.l && styles.purityTextActiveSilver]}>{o.l} ({o.t})</Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  const renderGoldPurity = () => {
    const opts = [
      { l: '14K', t: '58.3', r: liveRates?.gold14k || 45000 },
      { l: '18K', t: '75.0', r: liveRates?.gold18k || 55000 },
      { l: '20K', t: '83.3', r: 61000 },
      { l: '22K', t: '91.6', r: liveRates?.gold22k || 72500 },
      { l: '24K', t: '99.9', r: liveRates?.gold24k || 76000 },
    ];
    return (
      <View style={styles.purityRow}>
        {opts.map(o => (
          <TouchableOpacity 
            key={o.l} 
            style={[styles.purityBtn, gCategory === o.l && styles.purityBtnActive]}
            onPress={() => { setGCategory(o.l); setGTouch(o.t); setGRate(o.r.toString()); }}
          >
            <Text style={[styles.purityText, gCategory === o.l && styles.purityTextActive]}>{o.l}</Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  const isEditing = Boolean(initialItem);
  const finalBtnLabel = isEditing ? "✓ UPDATE ITEM" : buttonLabel;

  return (
    <View style={[styles.container, isEditing && styles.containerEditing]}>
      {isEditing && (
        <View style={styles.editingBanner}>
          <Text style={styles.editingBannerText}>✎ Editing Item</Text>
          {onCancelEdit && (
            <TouchableOpacity onPress={onCancelEdit} style={styles.cancelEditHeaderBtn}>
              <Text style={styles.cancelEditHeaderText}>✕ Cancel</Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      {/* Metal Toggle */}
      <View style={styles.toggleRow}>
        <TouchableOpacity style={[styles.toggleBtn, metal === 'Gold' ? styles.goldActive : styles.inactive]} onPress={() => setMetal('Gold')}>
          <Text style={[styles.toggleText, metal === 'Gold' && {color: '#000'}]}>🏅 GOLD</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.toggleBtn, metal === 'Silver' ? styles.silverActive : styles.inactive]} onPress={() => setMetal('Silver')}>
          <Text style={[styles.toggleText, metal === 'Silver' && {color: '#000'}]}>🥈 SILVER</Text>
        </TouchableOpacity>
      </View>

      <TextInput 
        style={styles.inputFull} 
        placeholder="Item Name / Description" 
        placeholderTextColor="#666"
        value={itemName} 
        onChangeText={setItemName} 
      />

      {metal === 'Gold' && (
        <View style={{ marginBottom: 12 }}>
          <Text style={styles.label}>Gold Purity</Text>
          {renderGoldPurity()}
        </View>
      )}
      
      {metal === 'Silver' && (
        <View style={{ marginBottom: 12 }}>
          <Text style={styles.label}>Silver Purity</Text>
          {renderSilverPurity()}
        </View>
      )}

      {/* Row 1 */}
      <View style={styles.row3}>
        <View style={styles.col}>
          <Text style={styles.label}>Gross Wt(g)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={metal === 'Gold' ? gGross : sGross} onChangeText={metal === 'Gold' ? setGGross : setSGross} />
        </View>
        <View style={styles.col}>
          <Text style={styles.label}>Stone Wt(g)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={metal === 'Gold' ? gStone : sStone} onChangeText={metal === 'Gold' ? setGStone : setSStone} />
        </View>
        <View style={styles.col}>
          <Text style={styles.label}>Net Wt(g)</Text>
          <View style={styles.disabledInput}><Text style={styles.disabledText}>{c.net.toFixed(3)}</Text></View>
        </View>
      </View>

      {/* Row 2 */}
      <View style={styles.row3}>
        <View style={styles.col}>
          <Text style={styles.label}>Touch %</Text>
          <TextInput style={[styles.input, {color:'#d4af37'}]} keyboardType="numeric" value={metal === 'Gold' ? gTouch : sTouch} onChangeText={metal === 'Gold' ? setGTouch : setSTouch} />
        </View>
        <View style={styles.col}>
          <Text style={styles.label}>Wastage %</Text>
          <TextInput style={[styles.input, {color:'#d4af37'}]} keyboardType="numeric" value={metal === 'Gold' ? gWastage : sWastage} onChangeText={metal === 'Gold' ? setGWastage : setSWastage} />
        </View>
        <View style={styles.col}>
          <Text style={styles.label}>Fine Wt(g)</Text>
          <View style={styles.disabledInput}><Text style={[styles.disabledText, {color:'#d4af37'}]}>{c.fine.toFixed(3)}</Text></View>
        </View>
      </View>

      {/* Row 3 */}
      <View style={styles.row2}>
        <View style={styles.col}>
          <Text style={styles.label}>Rate</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={metal === 'Gold' ? gRate : sRate} onChangeText={metal === 'Gold' ? setGRate : setSRate} />
        </View>
        <View style={styles.col}>
          <Text style={styles.label}>Metal Value</Text>
          <View style={styles.disabledInput}><Text style={styles.disabledText}>₹{c.metalVal.toFixed(2)}</Text></View>
        </View>
      </View>

      <View style={styles.divider} />
      <Text style={styles.sectionTitle}>CHARGES</Text>

      {/* Making Charge Type */}
      <View style={styles.makingTypeRow}>
        <Text style={styles.label}>MAKING TYPE</Text>
        <View style={styles.typeSelector}>
          {[ {l: '%', v: 'percent'}, {l: '₹/g', v: 'per_gm'}, {l: '₹ Flat', v: 'flat'} ].map(t => {
            const isSelected = metal === 'Gold' ? gMakingType === t.v : sMakingType === t.v;
            return (
              <TouchableOpacity 
                key={t.v}
                style={[styles.typeBtn, isSelected && styles.typeBtnActive]}
                onPress={() => metal === 'Gold' ? setGMakingType(t.v as any) : setSMakingType(t.v as any)}
              >
                <Text style={[styles.typeText, isSelected && styles.typeTextActive]}>{t.l}</Text>
              </TouchableOpacity>
            )
          })}
        </View>
      </View>

      <View style={styles.row2}>
        <View style={styles.col}>
          <Text style={styles.label}>Making Value</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={metal === 'Gold' ? gMakingValue : sMakingValue} onChangeText={metal === 'Gold' ? setGMakingValue : setSMakingValue} />
        </View>
        <View style={styles.col}>
          <Text style={styles.label}>Total Making</Text>
          <View style={styles.disabledInput}><Text style={styles.disabledText}>₹{c.makingTotal.toFixed(2)}</Text></View>
        </View>
      </View>

      <View style={styles.row2}>
        <View style={styles.col}>
          <Text style={styles.label}>Hallmark (+)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={metal === 'Gold' ? gHallmark : sHallmark} onChangeText={metal === 'Gold' ? setGHallmark : setSHallmark} />
        </View>
        <View style={styles.col}>
          <Text style={styles.label}>Other (+)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={metal === 'Gold' ? gOther : sOther} onChangeText={metal === 'Gold' ? setGOther : setSOther} />
        </View>
      </View>

      <View style={{ marginBottom: 16 }}>
        <Text style={[styles.label, {color: '#ef4444'}]}>Discount (-)</Text>
        <TextInput style={[styles.input, {borderColor: '#450a0a', backgroundColor: '#2e1010'}]} keyboardType="numeric" value={metal === 'Gold' ? gDiscount : sDiscount} onChangeText={metal === 'Gold' ? setGDiscount : setSDiscount} />
      </View>

      <View style={styles.taxableRow}>
        <Text style={styles.taxableLabel}>Taxable Amount</Text>
        <Text style={styles.taxableValue}>₹{c.taxAmt.toFixed(2)}</Text>
      </View>

      <View style={styles.buttonActionRow}>
        {isEditing && onCancelEdit && (
          <TouchableOpacity style={styles.cancelEditBtn} onPress={onCancelEdit}>
            <Text style={styles.cancelEditBtnText}>Cancel</Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity style={[styles.addButton, isEditing && styles.updateButton, isEditing && onCancelEdit && { flex: 2 }]} onPress={handleAdd}>
          <Text style={[styles.addButtonText, isEditing && styles.updateButtonText]}>{finalBtnLabel}</Text>
        </TouchableOpacity>
      </View>

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#111115',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#333',
    padding: 16,
    marginBottom: 20
  },
  containerEditing: {
    borderColor: '#d4af37',
    borderWidth: 1.5,
    backgroundColor: '#141416'
  },
  editingBanner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'rgba(212, 175, 55, 0.15)',
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 6,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#d4af37'
  },
  editingBannerText: {
    color: '#d4af37',
    fontSize: 12,
    fontWeight: '800'
  },
  cancelEditHeaderBtn: {
    paddingVertical: 2,
    paddingHorizontal: 6
  },
  cancelEditHeaderText: {
    color: '#ef4444',
    fontSize: 11,
    fontWeight: '700'
  },
  toggleRow: {
    flexDirection: 'row',
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 16
  },
  toggleBtn: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center'
  },
  goldActive: { backgroundColor: '#d4af37' },
  silverActive: { backgroundColor: '#e5e7eb' },
  inactive: { backgroundColor: '#1f2025' },
  toggleText: { fontSize: 12, fontWeight: 'bold', color: '#888' },
  
  inputFull: {
    backgroundColor: '#1a1a20',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 6,
    color: '#fff',
    padding: 10,
    marginBottom: 16
  },
  purityRow: { flexDirection: 'row', gap: 8, flexWrap: 'wrap' },
  purityBtn: { borderWidth: 1, borderColor: '#444', borderRadius: 4, paddingHorizontal: 10, paddingVertical: 4, backgroundColor: '#1a1a20' },
  purityBtnActive: { borderColor: '#d4af37', backgroundColor: 'rgba(212, 175, 55, 0.1)' },
  purityBtnActiveSilver: { borderColor: '#e5e7eb', backgroundColor: 'rgba(229, 231, 235, 0.1)' },
  purityText: { color: '#888', fontSize: 11, fontWeight: 'bold' },
  purityTextActive: { color: '#d4af37' },
  purityTextActiveSilver: { color: '#e5e7eb' },

  row3: { flexDirection: 'row', gap: 10, marginBottom: 12 },
  row2: { flexDirection: 'row', gap: 10, marginBottom: 12 },
  col: { flex: 1 },
  label: { color: '#888', fontSize: 10, textTransform: 'uppercase', fontWeight: 'bold', marginBottom: 4 },
  
  input: {
    backgroundColor: '#1a1a20',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 6,
    color: '#fff',
    padding: 8,
    fontFamily: 'monospace',
    fontSize: 13
  },
  disabledInput: {
    backgroundColor: '#0a0a0c',
    borderWidth: 1,
    borderColor: '#222',
    borderRadius: 6,
    padding: 8,
    justifyContent: 'center'
  },
  disabledText: { color: '#666', fontFamily: 'monospace', fontSize: 13 },
  
  divider: { height: 1, backgroundColor: '#333', marginVertical: 12 },
  sectionTitle: { color: '#666', fontSize: 10, fontWeight: 'bold', letterSpacing: 1, marginBottom: 12 },
  
  makingTypeRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  typeSelector: { flexDirection: 'row', backgroundColor: '#1a1a20', borderRadius: 4, borderWidth: 1, borderColor: '#333' },
  typeBtn: { paddingHorizontal: 12, paddingVertical: 4 },
  typeBtnActive: { backgroundColor: '#d4af37' },
  typeText: { color: '#888', fontSize: 10, fontWeight: 'bold' },
  typeTextActive: { color: '#000' },

  taxableRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  taxableLabel: { color: '#aaa', fontSize: 12 },
  taxableValue: { color: '#d4af37', fontSize: 18, fontWeight: 'bold', fontFamily: 'monospace' },
  
  buttonActionRow: {
    flexDirection: 'row',
    gap: 8
  },
  cancelEditBtn: {
    flex: 1,
    backgroundColor: '#333',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center'
  },
  cancelEditBtnText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 13
  },
  addButton: {
    flex: 1,
    backgroundColor: '#d4af37',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center'
  },
  addButtonText: { color: '#000', fontWeight: 'bold', fontSize: 14 },
  updateButton: {
    backgroundColor: '#22c55e'
  },
  updateButtonText: {
    color: '#000',
    fontWeight: '900'
  }
});
