import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, Modal, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function CreatePurchaseScreen({ navigation }: any) {
  const [sellers, setSellers] = useState<any[]>([]);
  const [selectedSeller, setSelectedSeller] = useState<any>(null);
  
  // Modals
  const [showSellerModal, setShowSellerModal] = useState(false);
  const [showAddSellerModal, setShowAddSellerModal] = useState(false);
  
  // New Supplier Form
  const [newSellerName, setNewSellerName] = useState('');
  const [newSellerPhone, setNewSellerPhone] = useState('');
  
  // Cart
  const [items, setItems] = useState<any[]>([]);
  
  // Form State
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [itemName, setItemName] = useState('');
  const [itemType, setItemType] = useState<'Gold' | 'Silver'>('Gold');
  const [grossWeight, setGrossWeight] = useState('');
  const [stoneWeight, setStoneWeight] = useState('');
  const [purity, setPurity] = useState('100'); 
  const [wastage, setWastage] = useState('0');
  const [rate, setRate] = useState('');
  const [labourCharge, setLabourCharge] = useState('0');
  const [otherCharges, setOtherCharges] = useState('0');
  const [hallmarkCharge, setHallmarkCharge] = useState('0');
  const [discount, setDiscount] = useState('0');
  const [makingChargeType, setMakingChargeType] = useState<'percent'|'per_gm'|'flat'>('flat');
  const [makingChargeValue, setMakingChargeValue] = useState('0');

  useEffect(() => {
    fetchSellers();
  }, []);

  const fetchSellers = async () => {
    try {
      const response = await axiosClient.get('/sellers/');
      setSellers(response.data.items || response.data || []);
    } catch (error) {
      console.log('Failed to fetch sellers', error);
    }
  };

  const handleAddNewSeller = async () => {
    if (!newSellerName) {
      Alert.alert('Error', 'Please enter a name');
      return;
    }

    // Clean and validate mobile number (10 or 12 digits)
    const cleanedPhone = newSellerPhone.replace(/\D/g, '');
    if (cleanedPhone.length !== 10 && cleanedPhone.length !== 12) {
      Alert.alert('Error', 'Mobile number must be exactly 10 digits, or 12 digits with country code');
      return;
    }

    try {
      const response = await axiosClient.post('/sellers/', {
        name: newSellerName,
        mobile: cleanedPhone,
      });
      const newSeller = response.data;
      setSellers([newSeller, ...sellers]);
      setSelectedSeller(newSeller);
      setShowAddSellerModal(false);
      setShowSellerModal(false);
      setNewSellerName('');
      setNewSellerPhone('');
    } catch (error) {
      console.log('Failed to add supplier', error);
      Alert.alert('Error', 'Failed to add supplier');
    }
  };

  const calculateMetal = () => {
    const gw = parseFloat(grossWeight) || 0;
    const sw = parseFloat(stoneWeight) || 0;
    const nw = Math.max(0, gw - sw);
    
    const pur = parseFloat(purity) || 0;
    const was = parseFloat(wastage) || 0;
    const fw = nw * ((pur + was) / 100);
    
    const rt = parseFloat(rate) || 0;
    const divider = itemType === 'Gold' ? 10 : 1000;
    const metalVal = fw * (rt / divider);
    
    const mval = parseFloat(makingChargeValue) || 0;
    let makingTotal = 0;
    if (makingChargeType === 'percent') { makingTotal = metalVal * (mval / 100); }
    else if (makingChargeType === 'per_gm') { makingTotal = nw * mval; }
    else { makingTotal = mval; }
    
    const lc = (parseFloat(labourCharge) || 0) + makingTotal;
    const oc = parseFloat(otherCharges) || 0;
    const hc = parseFloat(hallmarkCharge) || 0;
    const disc = parseFloat(discount) || 0;
    
    const taxable = metalVal + lc + oc + hc - disc;
    
    return {
      net_weight: nw,
      fine_weight: fw,
      metal_value: metalVal,
      taxable_amount: taxable
    };
  };

  const curCalc = calculateMetal();

  const handleAddOrUpdateItem = () => {
    if (!itemName) {
      Alert.alert('Error', 'Please enter item description');
      return;
    }
    
    const newItem = {
      metal_type: itemType,
      item_name: itemName,
      gross_weight: parseFloat(grossWeight) || 0,
      stone_weight: parseFloat(stoneWeight) || 0,
      net_weight: curCalc.net_weight,
      touch_purity: parseFloat(purity) || 0,
      wastage: parseFloat(wastage) || 0,
      fine_weight: curCalc.fine_weight,
      metal_rate: parseFloat(rate) || 0,
      metal_value: curCalc.metal_value,
      labour_charge: curCalc.taxable_amount - curCalc.metal_value - (parseFloat(otherCharges) || 0) - (parseFloat(hallmarkCharge) || 0) + (parseFloat(discount) || 0),
      hallmark_charge: parseFloat(hallmarkCharge) || 0,
      other_charges: parseFloat(otherCharges) || 0,
      discount: parseFloat(discount) || 0,
      taxable_amount: curCalc.taxable_amount
    };

    if (editIndex !== null) {
      const updatedItems = [...items];
      updatedItems[editIndex] = newItem;
      setItems(updatedItems);
      setEditIndex(null);
    } else {
      setItems([...items, newItem]);
    }
    
    // Reset Form
    setItemName('');
    setGrossWeight('');
    setStoneWeight('');
    setPurity('100');
    setWastage('0');
    setMakingChargeValue('0');
    setLabourCharge('0');
    setOtherCharges('0');
    setHallmarkCharge('0');
    setDiscount('0');
  };

  const handleEditItem = (index: number) => {
    const item = items[index];
    setItemType(item.metal_type as 'Gold'|'Silver');
    setItemName(item.item_name);
    setGrossWeight(item.gross_weight.toString());
    setStoneWeight(item.stone_weight.toString());
    setPurity(item.touch_purity.toString());
    setWastage(item.wastage.toString());
    setRate(item.metal_rate.toString());
    setLabourCharge(item.labour_charge.toString());
    setOtherCharges(item.other_charges.toString());
    setHallmarkCharge(item.hallmark_charge ? item.hallmark_charge.toString() : '0');
    setDiscount(item.discount ? item.discount.toString() : '0');
    setMakingChargeValue('0');
    setEditIndex(index);
  };

  const removeItem = (index: number) => {
    const newItems = [...items];
    newItems.splice(index, 1);
    setItems(newItems);
  };

  const subtotal = items.reduce((sum, item) => sum + item.taxable_amount, 0);
  const tax = subtotal * 0.03; // 3% GST standard
  const grandTotal = subtotal + tax;

  const handleProceed = () => {
    if (items.length === 0) {
      Alert.alert('Error', 'Please add at least one item');
      return;
    }
    navigation.navigate('CheckoutPurchase', {
      seller: selectedSeller,
      items: items
    });
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        
        {/* Supplier Selection */}
        <Text style={styles.label}>Select Supplier</Text>
        <TouchableOpacity style={styles.selector} onPress={() => setShowSellerModal(true)}>
          <Text style={styles.selectorText}>
            {selectedSeller ? `${selectedSeller.name}` : 'Walk-in Supplier (Tap to select)'}
          </Text>
        </TouchableOpacity>

        {/* Add Item Section */}
        <View style={styles.addItemCard}>
          <Text style={styles.cardTitle}>{editIndex !== null ? 'Edit Item' : 'Item Calculator'}</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Item Description (e.g. Gold Biscuit)"
            placeholderTextColor="#888"
            value={itemName}
            onChangeText={setItemName}
          />
          
          <View style={styles.typeSelector}>
            {(['Gold', 'Silver'] as any[]).map(type => (
              <TouchableOpacity 
                key={type}
                style={[styles.typeBtn, itemType === type && (type === 'Gold' ? styles.goldBtn : styles.silverBtn)]}
                onPress={() => setItemType(type)}
              >
                <Text style={[styles.typeBtnText, itemType === type && styles.typeBtnTextActive]}>{type}</Text>
              </TouchableOpacity>
            ))}
          </View>
          
          <View style={{ marginTop: 12 }}>
            <View style={styles.row}>
              <View style={styles.col}><Text style={styles.lbl}>Gross (g)</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={grossWeight} onChangeText={setGrossWeight}/></View>
              <View style={styles.col}><Text style={styles.lbl}>Stone (g)</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={stoneWeight} onChangeText={setStoneWeight}/></View>
              <View style={styles.col}><Text style={styles.lbl}>Net (g)</Text><View style={styles.readonly}><Text style={styles.readonlyText}>{curCalc.net_weight.toFixed(3)}</Text></View></View>
            </View>
            
            <View style={styles.row}>
              <View style={styles.col}><Text style={styles.lbl}>Touch/Tanch</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={purity} onChangeText={setPurity}/></View>
              <View style={styles.col}><Text style={styles.lbl}>Wastage %</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={wastage} onChangeText={setWastage}/></View>
              <View style={styles.col}><Text style={styles.lbl}>Fine (g)</Text><View style={styles.readonly}><Text style={styles.readonlyText}>{curCalc.fine_weight.toFixed(3)}</Text></View></View>
            </View>

            <View style={styles.row}>
              <View style={styles.col}><Text style={styles.lbl}>Making Type</Text>
                <View style={[styles.typeSelector, { marginBottom: 0 }]}>
                  {([ {label: '%', val: 'percent'}, {label: '₹/g', val: 'per_gm'}, {label: '₹ Flat', val: 'flat'} ] as any[]).map(t => (
                    <TouchableOpacity 
                      key={t.val}
                      style={[styles.typeBtn, makingChargeType === t.val && styles.goldBtn, { paddingVertical: 4 }]}
                      onPress={() => setMakingChargeType(t.val)}
                    >
                      <Text style={[styles.typeBtnText, { fontSize: 10 }, makingChargeType === t.val && styles.typeBtnTextActive]}>{t.label}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
              <View style={styles.col}><Text style={styles.lbl}>Making Value</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={makingChargeValue} onChangeText={setMakingChargeValue}/></View>
            </View>

            <View style={styles.row}>
              <View style={styles.col}><Text style={styles.lbl}>Rate (per {itemType === 'Gold' ? '10g' : '1kg'})</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={rate} onChangeText={setRate}/></View>
              <View style={styles.col}><Text style={styles.lbl}>Addt. Labour (+)</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={labourCharge} onChangeText={setLabourCharge}/></View>
              <View style={styles.col}><Text style={styles.lbl}>Other (+)</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={otherCharges} onChangeText={setOtherCharges}/></View>
            </View>
            
            <View style={styles.row}>
              <View style={styles.col}><Text style={styles.lbl}>Hallmark (+)</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={hallmarkCharge} onChangeText={setHallmarkCharge}/></View>
              <View style={styles.col}><Text style={styles.lbl}>Discount (-)</Text><TextInput style={[styles.inputSmall, { color: '#ef4444', borderColor: '#ef4444' }]} keyboardType="numeric" value={discount} onChangeText={setDiscount}/></View>
              <View style={styles.col}></View>
            </View>
            
            <View style={styles.calcResult}>
              <Text style={styles.calcResultLabel}>Taxable Amount</Text>
              <Text style={styles.calcResultValue}>₹ {curCalc.taxable_amount.toLocaleString('en-IN', {maximumFractionDigits: 2})}</Text>
            </View>
          </View>
          
          <TouchableOpacity style={[styles.addButton, editIndex !== null && {backgroundColor: '#d4af37'}]} onPress={handleAddOrUpdateItem}>
            <Text style={[styles.addButtonText, editIndex !== null && {color: '#000'}]}>
              {editIndex !== null ? 'Update Item' : '+ Add to Purchase'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Cart List */}
        <Text style={styles.label}>Purchase Items ({items.length})</Text>
        {items.map((item, index) => (
          <TouchableOpacity key={index} style={styles.cartItem} onPress={() => handleEditItem(index)}>
            <View>
              <Text style={styles.cartItemName}>{item.item_name} <Text style={styles.editHint}>(Tap to edit)</Text></Text>
              <Text style={styles.cartItemType}>
                {item.metal_type} | Net: {item.net_weight}g | Fine: {item.fine_weight.toFixed(3)}g
              </Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={styles.cartItemPrice}>₹ {item.taxable_amount.toLocaleString('en-IN', {maximumFractionDigits: 2})}</Text>
              <TouchableOpacity onPress={() => removeItem(index)} style={{ padding: 4, marginTop: 4 }}>
                <Text style={styles.removeText}>Remove</Text>
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        ))}

        {/* Totals */}
        <View style={styles.totalsCard}>
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Subtotal</Text>
            <Text style={styles.totalValue}>₹ {subtotal.toLocaleString('en-IN', {maximumFractionDigits: 2})}</Text>
          </View>
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Tax (3% GST)</Text>
            <Text style={styles.totalValue}>₹ {tax.toLocaleString('en-IN', {maximumFractionDigits: 2})}</Text>
          </View>
          <View style={[styles.totalRow, styles.grandTotalRow]}>
            <Text style={styles.grandTotalLabel}>Grand Total</Text>
            <Text style={styles.grandTotalValue}>₹ {grandTotal.toLocaleString('en-IN', {maximumFractionDigits: 2})}</Text>
          </View>
        </View>

        {/* Save Button */}
        <TouchableOpacity 
          style={[styles.saveButton, (items.length === 0) && styles.saveButtonDisabled]} 
          onPress={handleProceed}
          disabled={items.length === 0}
        >
          <Text style={styles.saveButtonText}>Proceed to Checkout →</Text>
        </TouchableOpacity>
        
        <View style={{ height: 40 }} />
      </ScrollView>

      {/* Supplier Picker Modal */}
      <Modal visible={showSellerModal} animationType="slide" transparent={true}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Select Supplier</Text>
            
            <TouchableOpacity style={styles.addNewBtn} onPress={() => setShowAddSellerModal(true)}>
              <Text style={styles.addNewBtnText}>+ Add New Supplier</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.customerOption} onPress={() => { setSelectedSeller(null); setShowSellerModal(false); }}>
              <Text style={styles.customerOptionText}>-- Walk-in Supplier --</Text>
            </TouchableOpacity>
            <FlatList
              data={sellers}
              keyExtractor={(item) => item.id.toString()}
              renderItem={({ item }) => (
                <TouchableOpacity style={styles.customerOption} onPress={() => { setSelectedSeller(item); setShowSellerModal(false); }}>
                  <Text style={styles.customerOptionText}>{item.name} ({item.mobile})</Text>
                </TouchableOpacity>
              )}
            />
            <TouchableOpacity style={styles.modalCloseBtn} onPress={() => setShowSellerModal(false)}>
              <Text style={styles.modalCloseText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Add New Supplier Modal */}
      <Modal visible={showAddSellerModal} animationType="fade" transparent={true}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add New Supplier</Text>
            
            <TextInput
              style={styles.input}
              placeholder="Supplier Name"
              placeholderTextColor="#888"
              value={newSellerName}
              onChangeText={setNewSellerName}
            />
            <TextInput
              style={styles.input}
              placeholder="Mobile Number"
              placeholderTextColor="#888"
              keyboardType="phone-pad"
              value={newSellerPhone}
              onChangeText={setNewSellerPhone}
            />
            
            <View style={{ flexDirection: 'row', gap: 12, marginTop: 16 }}>
              <TouchableOpacity style={[styles.addButton, { flex: 1, backgroundColor: '#333' }]} onPress={() => setShowAddSellerModal(false)}>
                <Text style={styles.addButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.addButton, { flex: 1, backgroundColor: '#d4af37' }]} onPress={handleAddNewSeller}>
                <Text style={[styles.addButtonText, { color: '#000' }]}>Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        </KeyboardAvoidingView>
      </Modal>

    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  label: { color: '#888', fontSize: 12, textTransform: 'uppercase', marginBottom: 8, marginTop: 16, fontWeight: 'bold' },
  selector: { backgroundColor: '#141414', borderWidth: 1, borderColor: '#333', padding: 16, borderRadius: 8 },
  selectorText: { color: '#fff', fontSize: 16 },
  addItemCard: { backgroundColor: '#141414', borderWidth: 1, borderColor: '#333', padding: 16, borderRadius: 8, marginTop: 16 },
  cardTitle: { color: '#d4af37', fontSize: 16, fontWeight: 'bold', marginBottom: 12 },
  input: { backgroundColor: '#0a0a0a', color: '#fff', borderWidth: 1, borderColor: '#333', padding: 12, borderRadius: 8, marginBottom: 12 },
  row: { flexDirection: 'row', gap: 8, marginBottom: 8 },
  col: { flex: 1 },
  lbl: { color: '#888', fontSize: 10, textTransform: 'uppercase', marginBottom: 4 },
  inputSmall: { backgroundColor: '#0a0a0a', color: '#fff', borderWidth: 1, borderColor: '#333', padding: 8, borderRadius: 6, fontVariant: ['tabular-nums'] },
  readonly: { backgroundColor: '#1a1a1a', borderWidth: 1, borderColor: '#222', padding: 8, borderRadius: 6, alignItems: 'center' },
  readonlyText: { color: '#888', fontVariant: ['tabular-nums'] },
  typeSelector: { flexDirection: 'row', backgroundColor: '#0a0a0a', borderWidth: 1, borderColor: '#333', borderRadius: 8, overflow: 'hidden', marginBottom: 12 },
  typeBtn: { flex: 1, paddingVertical: 12, alignItems: 'center', borderRightWidth: 1, borderRightColor: '#333' },
  goldBtn: { backgroundColor: '#d4af37' },
  silverBtn: { backgroundColor: '#9ca3af' },
  typeBtnText: { color: '#888', fontSize: 12, fontWeight: 'bold' },
  typeBtnTextActive: { color: '#000' },
  calcResult: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#1a1a1a', padding: 12, borderRadius: 8, marginTop: 8 },
  calcResultLabel: { color: '#888', fontSize: 12 },
  calcResultValue: { color: '#4ade80', fontSize: 16, fontWeight: 'bold' },
  addButton: { backgroundColor: '#333', padding: 12, borderRadius: 8, alignItems: 'center', marginTop: 12 },
  addButtonText: { color: '#fff', fontWeight: 'bold' },
  cartItem: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: '#1a1a1a', padding: 12, borderRadius: 8, marginBottom: 8 },
  cartItemName: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  editHint: { color: '#d4af37', fontSize: 10, fontWeight: 'normal' },
  cartItemType: { color: '#888', fontSize: 12 },
  cartItemPrice: { color: '#d4af37', fontSize: 16, fontWeight: 'bold' },
  removeText: { color: '#ef4444', fontSize: 12 },
  totalsCard: { backgroundColor: '#141414', borderWidth: 1, borderColor: '#333', padding: 16, borderRadius: 8, marginTop: 16 },
  totalRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  totalLabel: { color: '#888', fontSize: 14 },
  totalValue: { color: '#fff', fontSize: 14, fontVariant: ['tabular-nums'] },
  grandTotalRow: { borderTopWidth: 1, borderTopColor: '#333', paddingTop: 8, marginTop: 4, marginBottom: 0 },
  grandTotalLabel: { color: '#d4af37', fontSize: 18, fontWeight: 'bold' },
  grandTotalValue: { color: '#d4af37', fontSize: 18, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  saveButton: { backgroundColor: '#d4af37', padding: 16, borderRadius: 8, alignItems: 'center', marginTop: 24 },
  saveButtonDisabled: { opacity: 0.5 },
  saveButtonText: { color: '#000', fontSize: 18, fontWeight: 'bold' },
  
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.8)', justifyContent: 'center', padding: 20 },
  modalContent: { backgroundColor: '#141414', borderRadius: 12, padding: 20, maxHeight: '80%', borderWidth: 1, borderColor: '#333' },
  modalTitle: { color: '#d4af37', fontSize: 20, fontWeight: 'bold', marginBottom: 16 },
  customerOption: { paddingVertical: 16, borderBottomWidth: 1, borderBottomColor: '#333' },
  customerOptionText: { color: '#fff', fontSize: 16 },
  modalCloseBtn: { marginTop: 16, padding: 16, alignItems: 'center', backgroundColor: '#333', borderRadius: 8 },
  modalCloseText: { color: '#fff', fontWeight: 'bold' },
  addNewBtn: { backgroundColor: 'rgba(212, 175, 55, 0.1)', borderWidth: 1, borderColor: '#d4af37', padding: 12, borderRadius: 8, marginBottom: 12, alignItems: 'center' },
  addNewBtnText: { color: '#d4af37', fontWeight: 'bold' }
});
