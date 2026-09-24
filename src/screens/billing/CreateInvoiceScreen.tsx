import React, { useState, useEffect, useMemo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, Modal, FlatList, TextInput, KeyboardAvoidingView, Platform } from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import MobileMetalCalculator, { ItemPayload } from '../../components/MobileMetalCalculator';

export default function CreateInvoiceScreen({ navigation }: any) {
  const [customers, setCustomers] = useState<any[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [showCustomerModal, setShowCustomerModal] = useState(false);
  const [showAddCustomerModal, setShowAddCustomerModal] = useState(false);
  
  const [newCustomerFirstName, setNewCustomerFirstName] = useState('');
  const [newCustomerPhone, setNewCustomerPhone] = useState('');
  
  const [items, setItems] = useState<any[]>([]);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  
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
    const cleanedPhone = newCustomerPhone.replace(/\D/g, '');
    if (cleanedPhone.length !== 10 && cleanedPhone.length !== 12) {
      Alert.alert('Error', 'Mobile number must be exactly 10 digits');
      return;
    }
    try {
      const response = await axiosClient.post('/customers/', { first_name: newCustomerFirstName, phone_number: cleanedPhone });
      const newCust = response.data;
      setCustomers([newCust, ...customers]);
      setSelectedCustomer(newCust);
      setShowAddCustomerModal(false);
      setShowCustomerModal(false);
      setNewCustomerFirstName('');
      setNewCustomerPhone('');
    } catch (error) {
      Alert.alert('Error', 'Failed to add customer');
    }
  };

  const editingPayload = useMemo<ItemPayload | null>(() => {
    if (editingIndex === null || !items[editingIndex]) return null;
    const it = items[editingIndex];
    const isGold = it.item_type === 'Gold';
    const calc = isGold ? it.gold_calculation : it.silver_calculation;
    return {
      metalType: isGold ? 'Gold' : 'Silver',
      itemName: it.item_name || '',
      category: isGold ? (calc?.touch_purity >= 99 ? '24K' : calc?.touch_purity >= 91 ? '22K' : calc?.touch_purity >= 83 ? '20K' : calc?.touch_purity >= 75 ? '18K' : '14K') : 'Fine',
      grossWeight: Number(calc?.gross_weight || it.gross_weight || 0),
      stoneWeight: Number(calc?.stone_weight || 0),
      netWeight: Number(calc?.net_weight || it.net_weight || 0),
      touchPurity: Number(calc?.touch_purity || calc?.tanch_percentage || (isGold ? 91.6 : 99.9)),
      wastage: Number(calc?.wastage || 0),
      fineWeight: Number(calc?.fine_weight || calc?.pure_weight || 0),
      metalRate: Number(calc?.applied_rate || 0),
      metalValue: Number(calc?.total_gold_value || calc?.total_silver_value || 0),
      makingChargeType: calc?.making_charge_type || 'flat',
      makingChargeValue: Number(calc?.making_charge_rate || 0),
      makingAmount: Number(calc?.making_charges_amount || 0),
      hallmarkCharge: Number(calc?.hallmark_charges || 0),
      otherCharges: Number(calc?.other_charges || 0),
      discount: Number(calc?.discount || 0),
      taxableAmount: Number(it.final_price || 0)
    };
  }, [editingIndex, items]);

  const handleAddItem = (calcItem: any) => {
    const isGold = calcItem.metalType === 'Gold';
    const newItem: any = {
      item_name: calcItem.itemName,
      item_type: calcItem.metalType,
      final_price: calcItem.taxableAmount,
    };
    
    if (isGold) {
      newItem.gold_calculation = {
        applied_rate: calcItem.metalRate,
        gross_weight: calcItem.grossWeight,
        stone_weight: calcItem.stoneWeight,
        net_weight: calcItem.netWeight,
        touch_purity: calcItem.touchPurity,
        wastage: calcItem.wastage,
        fine_weight: calcItem.fineWeight,
        making_charge_type: calcItem.makingChargeType,
        making_charge_rate: calcItem.makingChargeValue,
        making_charges_amount: calcItem.makingAmount,
        hallmark_charges: calcItem.hallmarkCharge,
        other_charges: calcItem.otherCharges,
        discount: calcItem.discount,
        total_gold_value: calcItem.metalValue
      };
    } else {
      newItem.silver_calculation = {
        applied_rate: calcItem.metalRate,
        gross_weight: calcItem.grossWeight,
        stone_weight: calcItem.stoneWeight,
        tanch_percentage: calcItem.touchPurity,
        wastage: calcItem.wastage,
        pure_weight: calcItem.fineWeight,
        making_charge_type: calcItem.makingChargeType,
        making_charge_rate: calcItem.makingChargeValue,
        making_charges_amount: calcItem.makingAmount,
        other_charges: calcItem.otherCharges,
        discount: calcItem.discount,
        total_silver_value: calcItem.metalValue
      };
    }
    
    if (editingIndex !== null) {
      const updated = [...items];
      updated[editingIndex] = newItem;
      setItems(updated);
      setEditingIndex(null);
    } else {
      setItems([...items, newItem]);
    }
  };

  const removeItem = (index: number) => {
    if (editingIndex === index) setEditingIndex(null);
    const updated = [...items];
    updated.splice(index, 1);
    setItems(updated);
  };

  const subtotal = items.reduce((acc, item) => acc + (Number(item.final_price) || 0), 0);

  const handleSave = () => {
    if (items.length === 0) {
      Alert.alert('Error', 'Please add at least one item');
      return;
    }
    navigation.navigate('Checkout', {
      items,
      subtotal,
      tax: 0,
      grandTotal: subtotal,
      selectedCustomer
    });
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        {/* Customer Selection */}
        <Text style={styles.label}>Select Customer</Text>
        <TouchableOpacity style={styles.selector} onPress={() => setShowCustomerModal(true)}>
          <Text style={styles.selectorText}>
            {selectedCustomer ? `${selectedCustomer.first_name} (${selectedCustomer.phone_number})` : '-- Select Walk-in Customer --'}
          </Text>
        </TouchableOpacity>

        <Text style={[styles.label, {marginTop: 20}]}>
          {editingIndex !== null ? '✎ Edit Cart Item' : 'Add Item to Bill'}
        </Text>
        
        {/* Unified Calculator Component with edit support */}
        <MobileMetalCalculator 
          onAdd={handleAddItem} 
          buttonLabel={editingIndex !== null ? "✓ UPDATE ITEM" : "ADD TO BILL"}
          initialItem={editingPayload}
          onCancelEdit={() => setEditingIndex(null)}
        />

        {/* Cart View */}
        {items.length > 0 && (
          <View style={{ marginTop: 24 }}>
            <Text style={styles.label}>Cart Items ({items.length})</Text>
            {items.map((item, idx) => (
              <View key={idx} style={[styles.cartItem, editingIndex === idx && styles.cartItemEditing]}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.cartItemName}>{item.item_name}</Text>
                  <Text style={styles.cartItemType}>{item.item_type}</Text>
                  <Text style={styles.cartItemPrice}>₹{Number(item.final_price || 0).toFixed(2)}</Text>
                </View>
                <View style={styles.cartItemActions}>
                  <TouchableOpacity style={styles.editItemBtn} onPress={() => setEditingIndex(idx)}>
                    <Text style={styles.editItemBtnText}>✎ Edit</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.removeItemBtn} onPress={() => removeItem(idx)}>
                    <Text style={styles.removeItemBtnText}>✕ Remove</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))}

            <View style={styles.totalsCard}>
              <View style={[styles.totalRow, styles.grandTotalRow]}>
                <Text style={styles.grandTotalLabel}>Grand Total</Text>
                <Text style={styles.grandTotalValue}>₹{subtotal.toFixed(2)}</Text>
              </View>
            </View>

            <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
              <Text style={styles.saveButtonText}>Proceed to Checkout →</Text>
            </TouchableOpacity>
          </View>
        )}
        
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
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add New Customer</Text>
            <TextInput style={styles.input} placeholder="First Name" placeholderTextColor="#888" value={newCustomerFirstName} onChangeText={setNewCustomerFirstName} />
            <TextInput style={styles.input} placeholder="Mobile Number" placeholderTextColor="#888" keyboardType="phone-pad" value={newCustomerPhone} onChangeText={setNewCustomerPhone} />
            
            <View style={{ flexDirection: 'row', gap: 12, marginTop: 16 }}>
              <TouchableOpacity style={[styles.addButton, { flex: 1, backgroundColor: '#333' }]} onPress={() => setShowAddCustomerModal(false)}>
                <Text style={styles.addButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.addButton, { flex: 1, backgroundColor: '#d4af37' }]} onPress={handleAddNewCustomer}>
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
  cartItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#262626'
  },
  cartItemEditing: {
    borderColor: '#d4af37',
    backgroundColor: '#221f14'
  },
  cartItemName: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  cartItemType: { color: '#888', fontSize: 12, marginTop: 2 },
  cartItemPrice: { color: '#d4af37', fontSize: 15, fontWeight: 'bold', marginTop: 2 },
  cartItemActions: {
    flexDirection: 'row',
    gap: 8,
    alignItems: 'center'
  },
  editItemBtn: {
    backgroundColor: 'rgba(212, 175, 55, 0.15)',
    borderWidth: 1,
    borderColor: '#d4af37',
    paddingVertical: 5,
    paddingHorizontal: 10,
    borderRadius: 6
  },
  editItemBtnText: { color: '#d4af37', fontSize: 12, fontWeight: 'bold' },
  removeItemBtn: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderWidth: 1,
    borderColor: '#ef4444',
    paddingVertical: 5,
    paddingHorizontal: 10,
    borderRadius: 6
  },
  removeItemBtnText: { color: '#ef4444', fontSize: 12, fontWeight: 'bold' },

  totalsCard: { backgroundColor: '#141414', borderWidth: 1, borderColor: '#333', padding: 16, borderRadius: 8, marginTop: 16 },
  totalRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  totalLabel: { color: '#888', fontSize: 14 },
  totalValue: { color: '#fff', fontSize: 14, fontVariant: ['tabular-nums'] },
  grandTotalRow: { borderTopWidth: 1, borderTopColor: '#333', paddingTop: 8, marginTop: 4, marginBottom: 0 },
  grandTotalLabel: { color: '#d4af37', fontSize: 18, fontWeight: 'bold' },
  grandTotalValue: { color: '#d4af37', fontSize: 18, fontWeight: 'bold', fontVariant: ['tabular-nums'] },
  saveButton: { backgroundColor: '#d4af37', padding: 16, borderRadius: 8, alignItems: 'center', marginTop: 24 },
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
  input: { backgroundColor: '#0a0a0a', color: '#fff', borderWidth: 1, borderColor: '#333', padding: 12, borderRadius: 8, marginBottom: 12 },
  addButton: { padding: 12, borderRadius: 8, alignItems: 'center' },
  addButtonText: { color: '#fff', fontWeight: 'bold' }
});
