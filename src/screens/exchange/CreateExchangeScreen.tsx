import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator, Modal, FlatList } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function CreateExchangeScreen({ navigation }: any) {
  const [customers, setCustomers] = useState<any[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [showCustomerModal, setShowCustomerModal] = useState(false);
  const [showAddCustomerModal, setShowAddCustomerModal] = useState(false);
  
  const [newCustomerFirstName, setNewCustomerFirstName] = useState('');
  const [newCustomerPhone, setNewCustomerPhone] = useState('');
  
  const [items, setItems] = useState<any[]>([]);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [itemDirection, setItemDirection] = useState<'Old' | 'New'>('New');
  const [itemName, setItemName] = useState('');
  const [itemType, setItemType] = useState<'Gold' | 'Silver' | 'Other'>('Gold');
  
  // Metal Calculation State
  const [grossWeight, setGrossWeight] = useState('');
  const [stoneWeight, setStoneWeight] = useState('');
  const [purity, setPurity] = useState('100'); // Touch or Tanch
  const [wastage, setWastage] = useState('0');
  const [rate, setRate] = useState(''); // rate per 10g for gold, per kg for silver
  const [makingCharge, setMakingCharge] = useState('0');
  const [otherPrice, setOtherPrice] = useState(''); // for "Other" items

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await axiosClient.get('/customers/');
      setCustomers(response.data.items || response.data || []);
    } catch (error) {
      console.log('Failed to fetch customers', error);
    }
  };

  const handleAddNewCustomer = async () => {
    if (!newCustomerFirstName) {
      Alert.alert('Error', 'Please enter a name');
      return;
    }
    
    // Clean and validate phone number (10 or 12 digits)
    const cleanedPhone = newCustomerPhone.replace(/\D/g, '');
    if (cleanedPhone.length !== 10 && cleanedPhone.length !== 12) {
      Alert.alert('Error', 'Phone number must be exactly 10 digits, or 12 digits with country code');
      return;
    }

    try {
      const response = await axiosClient.post('/customers/', {
        first_name: newCustomerFirstName,
        phone_number: cleanedPhone,
      });
      const newCust = response.data;
      setCustomers([newCust, ...customers]);
      setSelectedCustomer(newCust);
      setShowAddCustomerModal(false);
      setShowCustomerModal(false);
      setNewCustomerFirstName('');
      setNewCustomerPhone('');
    } catch (error) {
      console.log('Failed to add customer', error);
      Alert.alert('Error', 'Failed to add customer');
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
    const mc = parseFloat(makingCharge) || 0;
    
    let mv = 0;
    if (itemType === 'Gold') {
      mv = fw * (rt / 10);
    } else if (itemType === 'Silver') {
      mv = fw * (rt / 1000);
    }
    
    const finalPrice = mv + mc;
    
    return {
      netWeight: nw,
      fineWeight: fw,
      metalValue: mv,
      finalPrice: finalPrice
    };
  };

  const addItem = () => {
    let newItem: any = {};
    if (!itemName) {
      Alert.alert('Error', 'Please enter item description');
      return;
    }
    
    if (itemType === 'Other') {
      const p = parseFloat(otherPrice) || 0;
      if (p <= 0) {
        Alert.alert('Error', 'Invalid price');
        return;
      }
      setItems([...items, { item_name: itemName, item_type: 'Other', final_price: p }]);
    } else {
      const gw = parseFloat(grossWeight) || 0;
      if (gw <= 0) {
        Alert.alert('Error', 'Gross weight must be > 0');
        return;
      }
      
      const calc = calculateMetal();
      
      newItem = {
        item_name: itemName,
        item_type: itemType,
        direction: itemDirection,
        final_price: calc.finalPrice,
      };
      
      if (itemType === 'Gold') {
        newItem.gold_calculation = {
          applied_rate: parseFloat(rate) || 0,
          gross_weight: gw,
          stone_weight: parseFloat(stoneWeight) || 0,
          net_weight: calc.netWeight,
          touch_purity: parseFloat(purity) || 0,
          wastage: parseFloat(wastage) || 0,
          fine_weight: calc.fineWeight,
          making_charge_type: 'flat',
          making_charge_rate: 0,
          making_charges_amount: parseFloat(makingCharge) || 0,
          hallmark_charges: 0,
          other_charges: 0,
          discount: 0,
          total_gold_value: calc.metalValue
        };
      } else {
        newItem.silver_calculation = {
          applied_rate: parseFloat(rate) || 0,
          gross_weight: gw,
          stone_weight: parseFloat(stoneWeight) || 0,
          tanch_percentage: parseFloat(purity) || 0,
          wastage: parseFloat(wastage) || 0,
          pure_weight: calc.fineWeight,
          making_charge_type: 'flat',
          making_charge_rate: 0,
          making_charges_amount: parseFloat(makingCharge) || 0,
          other_charges: 0,
          discount: 0,
          total_silver_value: calc.metalValue
        };
      }
    }
      
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
    setOtherPrice('');
  };

  const handleEditItem = (index: number) => {
    const item = items[index];
    setItemType(item.item_type as 'Gold'|'Silver'|'Other');
    setItemName(item.item_name);
    
    if (item.item_type === 'Other') {
      setOtherPrice(item.final_price.toString());
    } else if (item.item_type === 'Gold') {
      const calc = item.gold_calculation;
      setGrossWeight(calc.gross_weight.toString());
      setStoneWeight(calc.stone_weight.toString());
      setPurity(calc.purity.toString());
      setWastage(calc.wastage.toString());
      setRate(calc.rate.toString());
      setMakingCharge(calc.making_charges_amount.toString());
    } else if (item.item_type === 'Silver') {
      const calc = item.silver_calculation;
      setGrossWeight(calc.gross_weight.toString());
      setStoneWeight(calc.stone_weight.toString());
      setPurity(calc.purity.toString());
      setWastage(calc.wastage.toString());
      setRate(calc.rate.toString());
      setMakingCharge(calc.making_charges_amount.toString());
    }
    
    setEditIndex(index);
  };

  const removeItem = (index: number) => {
    const newItems = [...items];
    newItems.splice(index, 1);
    setItems(newItems);
  };

  const subtotal = items.reduce((sum, item) => sum + item.final_price, 0);
  const tax = subtotal * 0.03; // 3% GST standard
  const grandTotal = subtotal + tax;

  const handleSave = () => {
    if (items.length === 0) {
      Alert.alert('Error', 'Please add at least one item');
      return;
    }
    
    // Navigate to checkout screen passing data
    navigation.navigate('CheckoutExchange', {
      items,
      subtotal,
      tax,
      grandTotal,
      selectedCustomer
    });
  };
  
  const curCalc = calculateMetal();

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        
        {/* Customer Selection */}
        <Text style={styles.label}>Select Customer</Text>
        <TouchableOpacity style={styles.selector} onPress={() => setShowCustomerModal(true)}>
          <Text style={styles.selectorText}>
            {selectedCustomer ? `${selectedCustomer.first_name} ${selectedCustomer.last_name || ''}` : 'Walk-in Customer (Tap to select)'}
          </Text>
        </TouchableOpacity>

        {/* Add Item Section */}
        <View style={styles.addItemCard}>
          <Text style={styles.cardTitle}>{editIndex !== null ? 'Edit Item' : 'Item Calculator'}</Text>
          
          <View style={[styles.typeSelector, { marginBottom: 16 }]}>
            {(['Old', 'New'] as any[]).map(dir => (
              <TouchableOpacity 
                key={dir}
                style={[styles.typeBtn, itemDirection === dir && (dir === 'New' ? styles.goldBtn : styles.silverBtn)]}
                onPress={() => setItemDirection(dir)}
              >
                <Text style={[styles.typeBtnText, itemDirection === dir && styles.typeBtnTextActive]}>
                  {dir === 'Old' ? 'Old Metal (From Customer)' : 'New Item (To Customer)'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <TextInput
            style={styles.input}
            placeholder="Item Description (e.g. Gold Ring)"
            placeholderTextColor="#888"
            value={itemName}
            onChangeText={setItemName}
          />
          
          <View style={styles.typeSelector}>
            {(['Gold', 'Silver', 'Other'] as any[]).map(type => (
              <TouchableOpacity 
                key={type}
                style={[styles.typeBtn, itemType === type && (type === 'Gold' ? styles.goldBtn : type === 'Silver' ? styles.silverBtn : styles.activeBtn)]}
                onPress={() => setItemType(type)}
              >
                <Text style={[styles.typeBtnText, itemType === type && styles.typeBtnTextActive]}>{type}</Text>
              </TouchableOpacity>
            ))}
          </View>
          
          {itemType === 'Other' ? (
            <TextInput
              style={styles.input}
              placeholder="Total Price (₹)"
              placeholderTextColor="#888"
              keyboardType="numeric"
              value={otherPrice}
              onChangeText={setOtherPrice}
            />
          ) : (
            <View style={{ marginTop: 12 }}>
              <View style={styles.row}>
                <View style={styles.col}><Text style={styles.lbl}>Gross (g)</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={grossWeight} onChangeText={setGrossWeight}/></View>
                <View style={styles.col}><Text style={styles.lbl}>Stone (g)</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={stoneWeight} onChangeText={setStoneWeight}/></View>
                <View style={styles.col}><Text style={styles.lbl}>Net (g)</Text><View style={styles.readonly}><Text style={styles.readonlyText}>{curCalc.netWeight.toFixed(3)}</Text></View></View>
              </View>
              
              <View style={styles.row}>
                <View style={styles.col}><Text style={styles.lbl}>{itemType === 'Gold' ? 'Touch %' : 'Tanch %'}</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={purity} onChangeText={setPurity}/></View>
                <View style={styles.col}><Text style={styles.lbl}>Wastage %</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={wastage} onChangeText={setWastage}/></View>
                <View style={styles.col}><Text style={styles.lbl}>Fine (g)</Text><View style={styles.readonly}><Text style={styles.readonlyText}>{curCalc.fineWeight.toFixed(3)}</Text></View></View>
              </View>
              
              <View style={styles.row}>
                <View style={styles.col}><Text style={styles.lbl}>Rate (₹/{itemType === 'Gold' ? '10g' : 'kg'})</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={rate} onChangeText={setRate}/></View>
                <View style={styles.col}><Text style={styles.lbl}>Making (Flat ₹)</Text><TextInput style={styles.inputSmall} keyboardType="numeric" value={makingCharge} onChangeText={setMakingCharge}/></View>
              </View>
              
              <View style={styles.calcResult}>
                <Text style={styles.calcResultLabel}>Calculated Item Price:</Text>
                <Text style={styles.calcResultValue}>₹ {curCalc.finalPrice.toLocaleString('en-IN', {maximumFractionDigits: 2})}</Text>
              </View>
            </View>
          )}
          
          <TouchableOpacity style={[styles.addButton, editIndex !== null && {backgroundColor: '#d4af37'}]} onPress={addItem}>
            <Text style={[styles.addButtonText, editIndex !== null && {color: '#000'}]}>
              {editIndex !== null ? 'Update Item' : '+ Add to Bill'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Cart List */}
        <Text style={styles.label}>Invoice Items ({items.length})</Text>
        {items.map((item, index) => (
          <TouchableOpacity key={index} style={styles.cartItem} onPress={() => handleEditItem(index)}>
            <View>
              <Text style={styles.cartItemName}>{item.item_name} <Text style={styles.editHint}>(Tap to edit)</Text></Text>
              <Text style={styles.cartItemType}>
                {item.item_type} 
                {item.gold_calculation && ` | Net: ${item.gold_calculation.net_weight}g`}
                {item.silver_calculation && ` | Net: ${item.silver_calculation.pure_weight}g`}
              </Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={styles.cartItemPrice}>₹ {item.final_price.toLocaleString('en-IN', {maximumFractionDigits: 2})}</Text>
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
          onPress={handleSave}
          disabled={items.length === 0}
        >
          <Text style={styles.saveButtonText}>Proceed to CheckoutExchange →</Text>
        </TouchableOpacity>
        
        <View style={{ height: 40 }} />
      </ScrollView>

      {/* Customer Picker Modal */}
      <Modal visible={showCustomerModal} animationType="slide" transparent={true}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Select Customer</Text>
            
            <TouchableOpacity style={styles.addNewBtn} onPress={() => setShowAddCustomerModal(true)}>
              <Text style={styles.addNewBtnText}>+ Add New Customer</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.customerOption} onPress={() => { setSelectedCustomer(null); setShowCustomerModal(false); }}>
              <Text style={styles.customerOptionText}>-- Walk-in Customer --</Text>
            </TouchableOpacity>
            <FlatList
              data={customers}
              keyExtractor={(item) => item.id.toString()}
              renderItem={({ item }) => (
                <TouchableOpacity style={styles.customerOption} onPress={() => { setSelectedCustomer(item); setShowCustomerModal(false); }}>
                  <Text style={styles.customerOptionText}>{item.first_name} {item.last_name || ''} ({item.phone_number})</Text>
                </TouchableOpacity>
              )}
            />
            <TouchableOpacity style={styles.modalCloseBtn} onPress={() => setShowCustomerModal(false)}>
              <Text style={styles.modalCloseText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Add New Customer Modal */}
      <Modal visible={showAddCustomerModal} animationType="fade" transparent={true}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add New Customer</Text>
            
            <TextInput
              style={styles.input}
              placeholder="First Name"
              placeholderTextColor="#888"
              value={newCustomerFirstName}
              onChangeText={setNewCustomerFirstName}
            />
            <TextInput
              style={styles.input}
              placeholder="Mobile Number"
              placeholderTextColor="#888"
              keyboardType="phone-pad"
              value={newCustomerPhone}
              onChangeText={setNewCustomerPhone}
            />
            
            <View style={{ flexDirection: 'row', gap: 12, marginTop: 16 }}>
              <TouchableOpacity style={[styles.addButton, { flex: 1, backgroundColor: '#333' }]} onPress={() => setShowAddCustomerModal(false)}>
                <Text style={styles.addButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.addButton, { flex: 1, backgroundColor: '#d4af37' }]} onPress={handleAddNewCustomer}>
                <Text style={[styles.addButtonText, { color: '#000' }]}>Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
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
  typeSelector: { flexDirection: 'row', backgroundColor: '#0a0a0a', borderWidth: 1, borderColor: '#333', borderRadius: 8, overflow: 'hidden' },
  typeBtn: { flex: 1, paddingVertical: 12, alignItems: 'center', borderRightWidth: 1, borderRightColor: '#333' },
  goldBtn: { backgroundColor: '#d4af37' },
  silverBtn: { backgroundColor: '#9ca3af' },
  activeBtn: { backgroundColor: '#333' },
  typeBtnText: { color: '#888', fontSize: 12, fontWeight: 'bold' },
  typeBtnTextActive: { color: '#000' },
  calcResult: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#1a1a1a', padding: 12, borderRadius: 8, marginTop: 8 },
  calcResultLabel: { color: '#888', fontSize: 12 },
  calcResultValue: { color: '#4ade80', fontSize: 16, fontWeight: 'bold' },
  addButton: { backgroundColor: '#333', padding: 12, borderRadius: 8, alignItems: 'center', marginTop: 12 },
  addButtonText: { color: '#fff', fontWeight: 'bold' },
  cartItem: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: '#1a1a1a', padding: 12, borderRadius: 8, marginBottom: 8 },
  cartItemName: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  cartItemType: { color: '#888', fontSize: 12 },
  cartItemPrice: { color: '#d4af37', fontSize: 16, fontWeight: 'bold' },
  removeText: { color: '#ef4444', fontSize: 12, marginTop: 4 },
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
  addNewBtnText: { color: '#d4af37', fontWeight: 'bold' },
  editHint: { color: '#d4af37', fontSize: 10, fontWeight: 'normal' }
});
