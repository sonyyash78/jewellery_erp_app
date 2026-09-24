import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, Modal, FlatList, TextInput, KeyboardAvoidingView, Platform } from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import MobileMetalCalculator from '../../components/MobileMetalCalculator';

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
    const cleanedPhone = newSellerPhone.replace(/\D/g, '');
    if (cleanedPhone.length !== 10 && cleanedPhone.length !== 12) {
      Alert.alert('Error', 'Mobile number must be exactly 10 digits');
      return;
    }
    try {
      const response = await axiosClient.post('/sellers/', { name: newSellerName, mobile: cleanedPhone });
      const newSeller = response.data;
      setSellers([newSeller, ...sellers]);
      setSelectedSeller(newSeller);
      setShowAddSellerModal(false);
      setShowSellerModal(false);
      setNewSellerName('');
      setNewSellerPhone('');
    } catch (error) {
      Alert.alert('Error', 'Failed to add supplier');
    }
  };

  const handleAddItem = (calcItem: any) => {
    // Map MobileMetalCalculator payload to backend expected structure
    const newItem = {
      metal_type: calcItem.metalType,
      item_name: calcItem.itemName,
      gross_weight: calcItem.grossWeight,
      stone_weight: calcItem.stoneWeight,
      net_weight: calcItem.netWeight,
      touch_purity: calcItem.touchPurity,
      wastage: calcItem.wastage,
      fine_weight: calcItem.fineWeight,
      metal_rate: calcItem.metalRate,
      metal_value: calcItem.metalValue,
      labour_charge: calcItem.makingAmount,
      hallmark_charge: calcItem.hallmarkCharge,
      other_charges: calcItem.otherCharges,
      discount: calcItem.discount,
      taxable_amount: calcItem.taxableAmount
    };
    
    setItems([...items, newItem]);
  };

  const removeItem = (index: number) => {
    const updated = [...items];
    updated.splice(index, 1);
    setItems(updated);
  };

  const subtotal = items.reduce((acc, item) => acc + item.taxable_amount, 0);
  const totalFineWeight = items.reduce((acc, item) => acc + item.fine_weight, 0);

  const handleSave = () => {
    if (items.length === 0) {
      Alert.alert('Error', 'Please add at least one item');
      return;
    }
    if (!selectedSeller) {
      setShowSellerModal(true);
      return;
    }
    navigation.navigate('CheckoutPurchase', {
      items,
      subtotal,
      totalFineWeight,
      selectedSeller
    });
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        {/* Supplier Selection */}
        <Text style={styles.label}>Select Supplier</Text>
        <TouchableOpacity style={styles.selector} onPress={() => setShowSellerModal(true)}>
          <Text style={styles.selectorText}>
            {selectedSeller ? `${selectedSeller.name} (${selectedSeller.mobile})` : '-- Select Supplier --'}
          </Text>
        </TouchableOpacity>

        <Text style={[styles.label, {marginTop: 20}]}>Add Item to Bill</Text>
        
        {/* Unified Calculator Component */}
        <MobileMetalCalculator onAdd={handleAddItem} buttonLabel="ADD TO BILL" />

        {/* Cart View */}
        {items.length > 0 && (
          <View style={{ marginTop: 24 }}>
            <Text style={styles.label}>Cart Items ({items.length})</Text>
            {items.map((item, idx) => (
              <View key={idx} style={styles.cartItem}>
                <View>
                  <Text style={styles.cartItemName}>{item.item_name}</Text>
                  <Text style={styles.cartItemType}>{item.metal_type} | Net: {item.net_weight}g | Fine: {item.fine_weight.toFixed(3)}g</Text>
                  <Text style={styles.cartItemPrice}>₹{item.taxable_amount.toFixed(2)}</Text>
                </View>
                <TouchableOpacity onPress={() => removeItem(idx)}>
                  <Text style={styles.removeText}>Remove</Text>
                </TouchableOpacity>
              </View>
            ))}

            <View style={styles.totalsCard}>
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>Total Fine Weight</Text>
                <Text style={styles.totalValue}>{totalFineWeight.toFixed(3)}g</Text>
              </View>
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

      {/* Supplier Picker Modal */}
      <Modal visible={showSellerModal} animationType="slide" transparent={true}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Select Supplier</Text>
            
            <TouchableOpacity style={styles.addNewBtn} onPress={() => setShowAddSellerModal(true)}>
              <Text style={styles.addNewBtnText}>+ Add New Supplier</Text>
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
            <TextInput style={styles.input} placeholder="Supplier Name" placeholderTextColor="#888" value={newSellerName} onChangeText={setNewSellerName} />
            <TextInput style={styles.input} placeholder="Mobile Number" placeholderTextColor="#888" keyboardType="phone-pad" value={newSellerPhone} onChangeText={setNewSellerPhone} />
            
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
