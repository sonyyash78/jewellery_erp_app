import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, Modal, FlatList, TextInput, KeyboardAvoidingView, Platform } from 'react-native';
import { axiosClient } from '../../api/axiosClient';
import MobileMetalCalculator from '../../components/MobileMetalCalculator';

export default function CreateExchangeScreen({ navigation }: any) {
  const [customers, setCustomers] = useState<any[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [showCustomerModal, setShowCustomerModal] = useState(false);
  const [showAddCustomerModal, setShowAddCustomerModal] = useState(false);
  
  const [newCustomerFirstName, setNewCustomerFirstName] = useState('');
  const [newCustomerPhone, setNewCustomerPhone] = useState('');
  
  // Two separate carts: New items (selling) and Old items (buying back)
  const [newItems, setNewItems] = useState<any[]>([]);
  const [oldItems, setOldItems] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'new' | 'old'>('new');

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

  const handleAddNewItem = (calcItem: any) => {
    const isGold = calcItem.metalType === 'Gold';
    const item: any = {
      item_name: calcItem.itemName,
      item_type: calcItem.metalType,
      direction: 'New',
      final_price: calcItem.taxableAmount,
    };
    if (isGold) {
      item.gold_calculation = {
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
        total_gold_value: calcItem.metalValue,
      };
    } else {
      item.silver_calculation = {
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
        total_silver_value: calcItem.metalValue,
      };
    }
    setNewItems([...newItems, item]);
  };

  const handleAddOldItem = (calcItem: any) => {
    const isGold = calcItem.metalType === 'Gold';
    const item: any = {
      item_name: calcItem.itemName,
      item_type: calcItem.metalType,
      direction: 'Old',
      final_price: calcItem.taxableAmount,
    };
    if (isGold) {
      item.gold_calculation = {
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
        total_gold_value: calcItem.metalValue,
      };
    } else {
      item.silver_calculation = {
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
        total_silver_value: calcItem.metalValue,
      };
    }
    setOldItems([...oldItems, item]);
  };

  const removeNewItem = (idx: number) => { const u = [...newItems]; u.splice(idx, 1); setNewItems(u); };
  const removeOldItem = (idx: number) => { const u = [...oldItems]; u.splice(idx, 1); setOldItems(u); };

  const newTotal = newItems.reduce((acc, i) => acc + i.final_price, 0);
  const oldTotal = oldItems.reduce((acc, i) => acc + i.final_price, 0);
  const payable = newTotal - oldTotal;

  const handleSave = () => {
    if (newItems.length === 0 && oldItems.length === 0) {
      Alert.alert('Error', 'Please add at least one item');
      return;
    }
    navigation.navigate('CheckoutExchange', {
      items: [...newItems, ...oldItems],
      newTotal,
      oldTotal,
      payable,
      selectedCustomer,
    });
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        {/* Customer Selection */}
        <Text style={styles.label}>Select Customer</Text>
        <TouchableOpacity style={styles.selector} onPress={() => setShowCustomerModal(true)}>
          <Text style={styles.selectorText}>
            {selectedCustomer ? `${selectedCustomer.first_name} (${selectedCustomer.phone_number})` : '-- Select Customer --'}
          </Text>
        </TouchableOpacity>

        {/* Direction Tabs */}
        <View style={styles.directionTabs}>
          <TouchableOpacity
            style={[styles.dirTab, activeTab === 'new' && styles.dirTabActiveNew]}
            onPress={() => setActiveTab('new')}
          >
            <Text style={[styles.dirTabText, activeTab === 'new' && { color: '#000' }]}>
              🆕 New Items (To Customer)
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.dirTab, activeTab === 'old' && styles.dirTabActiveOld]}
            onPress={() => setActiveTab('old')}
          >
            <Text style={[styles.dirTabText, activeTab === 'old' && { color: '#000' }]}>
              ♻️ Old Items (From Customer)
            </Text>
          </TouchableOpacity>
        </View>

        {/* Calculator based on active tab */}
        {activeTab === 'new' ? (
          <MobileMetalCalculator onAdd={handleAddNewItem} buttonLabel="ADD NEW ITEM" />
        ) : (
          <MobileMetalCalculator onAdd={handleAddOldItem} buttonLabel="ADD OLD ITEM" />
        )}

        {/* New Items Cart */}
        {newItems.length > 0 && (
          <View style={{ marginTop: 20 }}>
            <Text style={[styles.label, { color: '#4ade80' }]}>New Items ({newItems.length})</Text>
            {newItems.map((item, idx) => (
              <View key={`new-${idx}`} style={[styles.cartItem, { borderLeftWidth: 3, borderLeftColor: '#4ade80' }]}>
                <View>
                  <Text style={styles.cartItemName}>{item.item_name}</Text>
                  <Text style={styles.cartItemType}>{item.item_type}</Text>
                </View>
                <View style={{ alignItems: 'flex-end' }}>
                  <Text style={styles.cartItemPrice}>₹{item.final_price.toFixed(2)}</Text>
                  <TouchableOpacity onPress={() => removeNewItem(idx)}>
                    <Text style={styles.removeText}>Remove</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Old Items Cart */}
        {oldItems.length > 0 && (
          <View style={{ marginTop: 16 }}>
            <Text style={[styles.label, { color: '#f97316' }]}>Old Items ({oldItems.length})</Text>
            {oldItems.map((item, idx) => (
              <View key={`old-${idx}`} style={[styles.cartItem, { borderLeftWidth: 3, borderLeftColor: '#f97316' }]}>
                <View>
                  <Text style={styles.cartItemName}>{item.item_name}</Text>
                  <Text style={styles.cartItemType}>{item.item_type}</Text>
                </View>
                <View style={{ alignItems: 'flex-end' }}>
                  <Text style={[styles.cartItemPrice, { color: '#f97316' }]}>- ₹{item.final_price.toFixed(2)}</Text>
                  <TouchableOpacity onPress={() => removeOldItem(idx)}>
                    <Text style={styles.removeText}>Remove</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Settlement Summary */}
        {(newItems.length > 0 || oldItems.length > 0) && (
          <View style={styles.totalsCard}>
            <View style={styles.totalRow}>
              <Text style={styles.totalLabel}>New Items Total</Text>
              <Text style={[styles.totalValue, { color: '#4ade80' }]}>₹{newTotal.toFixed(2)}</Text>
            </View>
            <View style={styles.totalRow}>
              <Text style={styles.totalLabel}>Old Items Value</Text>
              <Text style={[styles.totalValue, { color: '#f97316' }]}>- ₹{oldTotal.toFixed(2)}</Text>
            </View>
            <View style={[styles.totalRow, styles.grandTotalRow]}>
              <Text style={styles.grandTotalLabel}>{payable >= 0 ? 'Customer Pays' : 'Shop Owes'}</Text>
              <Text style={[styles.grandTotalValue, payable < 0 && { color: '#ef4444' }]}>
                ₹{Math.abs(payable).toFixed(2)}
              </Text>
            </View>
          </View>
        )}

        <TouchableOpacity
          style={[styles.saveButton, (newItems.length === 0 && oldItems.length === 0) && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={newItems.length === 0 && oldItems.length === 0}
        >
          <Text style={styles.saveButtonText}>Proceed to Checkout →</Text>
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

  directionTabs: { flexDirection: 'row', marginTop: 20, marginBottom: 16, borderRadius: 8, overflow: 'hidden', borderWidth: 1, borderColor: '#333' },
  dirTab: { flex: 1, paddingVertical: 12, alignItems: 'center', backgroundColor: '#1a1a20' },
  dirTabActiveNew: { backgroundColor: '#4ade80' },
  dirTabActiveOld: { backgroundColor: '#f97316' },
  dirTabText: { fontSize: 11, fontWeight: 'bold', color: '#888' },

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
  input: { backgroundColor: '#0a0a0a', color: '#fff', borderWidth: 1, borderColor: '#333', padding: 12, borderRadius: 8, marginBottom: 12 },
  addButton: { padding: 12, borderRadius: 8, alignItems: 'center' },
  addButtonText: { color: '#fff', fontWeight: 'bold' },
});
