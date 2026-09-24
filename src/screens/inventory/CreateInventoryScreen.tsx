import React, { useState } from 'react';
import { Ionicons } from '@expo/vector-icons';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function CreateInventoryScreen({ navigation }: any) {
  const [formData, setFormData] = useState({
    item_name: '',
    category: '',
    metal: 'Gold',
    purity: '',
    hsn: '',
    gross_weight: '',
    stone_weight: '',
    net_weight: '',
    tanch: '',
    wastage: '',
    making_type: 'Flat',
    making_charge: '',
    hallmark: '',
    other_charges: '',
    location: '',
    shelf: '',
    status: 'Available',
    description: ''
  });
  
  const [loading, setLoading] = useState(false);

  // Derived calculations
  const gross = parseFloat(formData.gross_weight) || 0;
  const stone = parseFloat(formData.stone_weight) || 0;
  
  // If user typed net weight directly, use it, else calculate from gross - stone
  const calculatedNet = gross - stone > 0 ? (gross - stone) : 0;
  const net = formData.net_weight ? (parseFloat(formData.net_weight) || 0) : calculatedNet;

  const tanch = parseFloat(formData.tanch) || 0;
  const wastage = parseFloat(formData.wastage) || 0;
  const fine = net * ((tanch + wastage) / 100);

  const handleSubmit = async () => {
    if (!formData.item_name || !formData.category || !formData.gross_weight) {
      Alert.alert('Validation Error', 'Item Name, Category, and Gross Weight are required.');
      return;
    }

    try {
      setLoading(true);
      await axiosClient.post('/stock/', {
        item_name: formData.item_name,
        metal: formData.metal,
        category: formData.category,
        purity: formData.purity || undefined,
        hsn: formData.hsn || undefined,
        tanch: tanch || undefined,
        wastage: wastage || undefined,
        gross_weight: gross,
        stone_weight: stone,
        net_weight: net,
        making_type: formData.making_type,
        making_charge: parseFloat(formData.making_charge) || 0,
        hallmark: parseFloat(formData.hallmark) || 0,
        other_charges: parseFloat(formData.other_charges) || 0,
        location: formData.location || undefined,
        shelf: formData.shelf || undefined,
        description: formData.description || undefined,
        status: formData.status
      });
      Alert.alert('Success', 'Inventory item added successfully!');
      navigation.goBack();
    } catch (error: any) {
      console.log('Failed to create item', error.response?.data || error.message);
      Alert.alert('Error', 'Failed to add item to inventory.');
    } finally {
      setLoading(false);
    }
  };

  const SectionTitle = ({ title }: { title: string }) => (
    <Text style={styles.sectionTitle}>{title}</Text>
  );

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        
        {/* Basic Information */}
        <SectionTitle title="Basic Information" />
        <View style={styles.card}>
          <View style={styles.row}>
            <View style={styles.col}>
              <Text style={styles.label}>ITEM NAME *</Text>
              <TextInput style={styles.input} placeholder="e.g. Ring, Chain" placeholderTextColor="#555" value={formData.item_name} onChangeText={(t) => setFormData({ ...formData, item_name: t })} />
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>CATEGORY *</Text>
              <TextInput style={styles.input} placeholder="e.g. Ring, Chain" placeholderTextColor="#555" value={formData.category} onChangeText={(t) => setFormData({ ...formData, category: t })} />
            </View>
          </View>
          
          <View style={styles.row}>
            <View style={styles.col}>
              <Text style={styles.label}>METAL</Text>
              <View style={styles.radioGroup}>
                <TouchableOpacity style={[styles.radio, formData.metal === 'Gold' && styles.radioActive]} onPress={() => setFormData({ ...formData, metal: 'Gold' })}>
                  <Text style={styles.radioText}>Gold</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.radio, formData.metal === 'Silver' && styles.radioActive]} onPress={() => setFormData({ ...formData, metal: 'Silver' })}>
                  <Text style={styles.radioText}>Silver</Text>
                </TouchableOpacity>
              </View>
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>PURITY</Text>
              <TextInput style={styles.input} placeholder="22K916" placeholderTextColor="#555" value={formData.purity} onChangeText={(t) => setFormData({ ...formData, purity: t })} />
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>HSN CODE</Text>
              <TextInput style={styles.input} keyboardType="numeric" placeholderTextColor="#555" value={formData.hsn} onChangeText={(t) => setFormData({ ...formData, hsn: t })} />
            </View>
          </View>
        </View>

        {/* Weight & Purity Details */}
        <SectionTitle title="Weight & Purity Details" />
        <View style={styles.card}>
          <View style={styles.row}>
            <View style={styles.col}>
              <Text style={styles.label}>GROSS WT(G) *</Text>
              <TextInput style={styles.input} keyboardType="numeric" value={formData.gross_weight} onChangeText={(t) => setFormData({ ...formData, gross_weight: t })} />
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>STONE WT(G)</Text>
              <TextInput style={styles.input} keyboardType="numeric" value={formData.stone_weight} onChangeText={(t) => setFormData({ ...formData, stone_weight: t })} />
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>NET WT(G)</Text>
              <TextInput style={[styles.input, { color: '#d4af37' }]} keyboardType="numeric" placeholder={calculatedNet.toFixed(3)} placeholderTextColor="#d4af37" value={formData.net_weight} onChangeText={(t) => setFormData({ ...formData, net_weight: t })} />
            </View>
          </View>

          <View style={styles.row}>
            <View style={styles.col}>
              <Text style={styles.label}>TANCH (%)</Text>
              <TextInput style={styles.input} keyboardType="numeric" placeholder="e.g. 92" placeholderTextColor="#555" value={formData.tanch} onChangeText={(t) => setFormData({ ...formData, tanch: t })} />
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>WASTAGE (%)</Text>
              <TextInput style={styles.input} keyboardType="numeric" placeholder="e.g. 2" placeholderTextColor="#555" value={formData.wastage} onChangeText={(t) => setFormData({ ...formData, wastage: t })} />
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>FINE WT(G)</Text>
              <View style={styles.disabledInput}>
                <Text style={styles.disabledText}>{fine.toFixed(3)}</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Charges */}
        <SectionTitle title="Charges" />
        <View style={styles.card}>
          <View style={styles.row}>
            <View style={styles.col}>
              <Text style={styles.label}>MAKING TYPE</Text>
              <View style={styles.radioGroup}>
                <TouchableOpacity style={[styles.radio, formData.making_type === 'Flat' && styles.radioActive]} onPress={() => setFormData({ ...formData, making_type: 'Flat' })}>
                  <Text style={[styles.radioText, {fontSize: 12}]}>Flat</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.radio, formData.making_type === 'PerGram' && styles.radioActive]} onPress={() => setFormData({ ...formData, making_type: 'PerGram' })}>
                  <Text style={[styles.radioText, {fontSize: 12}]}>/g</Text>
                </TouchableOpacity>
              </View>
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>MAKING CHG</Text>
              <TextInput style={styles.input} keyboardType="numeric" value={formData.making_charge} onChangeText={(t) => setFormData({ ...formData, making_charge: t })} />
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>HALLMARK</Text>
              <TextInput style={styles.input} keyboardType="numeric" value={formData.hallmark} onChangeText={(t) => setFormData({ ...formData, hallmark: t })} />
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>OTHER CHG</Text>
              <TextInput style={styles.input} keyboardType="numeric" value={formData.other_charges} onChangeText={(t) => setFormData({ ...formData, other_charges: t })} />
            </View>
          </View>
        </View>

        {/* Storage & Status */}
        <SectionTitle title="Storage & Status" />
        <View style={styles.card}>
          <View style={styles.row}>
            <View style={styles.col}>
              <Text style={styles.label}>LOCATION</Text>
              <TextInput style={styles.input} placeholder="e.g. Main Store" placeholderTextColor="#555" value={formData.location} onChangeText={(t) => setFormData({ ...formData, location: t })} />
            </View>
            <View style={styles.col}>
              <Text style={styles.label}>SHELF / TRAY</Text>
              <TextInput style={styles.input} placeholder="e.g. Tray 5" placeholderTextColor="#555" value={formData.shelf} onChangeText={(t) => setFormData({ ...formData, shelf: t })} />
            </View>
          </View>
          
          <Text style={styles.label}>STATUS</Text>
          <View style={[styles.radioGroup, { marginBottom: 16 }]}>
            <TouchableOpacity style={[styles.radio, formData.status === 'Available' && styles.radioActive]} onPress={() => setFormData({ ...formData, status: 'Available' })}>
              <Text style={[styles.radioText, {fontSize: 11}]} numberOfLines={1}>Available</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.radio, formData.status === 'Low Stock' && styles.radioActive]} onPress={() => setFormData({ ...formData, status: 'Low Stock' })}>
              <Text style={[styles.radioText, {fontSize: 11}]} numberOfLines={1}>Low Stock</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.radio, formData.status === 'Not Available' && styles.radioActive]} onPress={() => setFormData({ ...formData, status: 'Not Available' })}>
              <Text style={[styles.radioText, {fontSize: 11}]} numberOfLines={1}>Not Available</Text>
            </TouchableOpacity>
          </View>
          
          <Text style={styles.label}>DESCRIPTION</Text>
          <TextInput 
            style={[styles.input, { height: 80, textAlignVertical: 'top' }]} 
            multiline 
            value={formData.description} 
            onChangeText={(t) => setFormData({ ...formData, description: t })} 
          />
        </View>

        {/* Action Buttons */}
        <View style={styles.actionRow}>
          <TouchableOpacity style={styles.cancelButton} onPress={() => navigation.goBack()}>
            <Text style={styles.cancelButtonText}>Cancel</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.submitButton} onPress={handleSubmit} disabled={loading}>
            {loading ? <ActivityIndicator color="#0a0a0a" /> : <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}><Ionicons name="qr-code-outline" size={16} color="#0a0a0a" /><Text style={styles.submitButtonText}>Save Item & Generate QR</Text></View>}
          </TouchableOpacity>
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
    marginTop: 8,
  },
  card: {
    backgroundColor: '#141414',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 20,
  },
  row: {
    flexDirection: 'row',
    marginBottom: 16,
    marginHorizontal: -4,
  },
  col: {
    flex: 1,
    paddingHorizontal: 4,
  },
  label: {
    color: '#888',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  input: {
    backgroundColor: '#0a0a0a',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 4,
    padding: 10,
    color: '#fff',
    fontSize: 14,
  },
  disabledInput: {
    backgroundColor: '#1a1a20',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 4,
    padding: 10,
    justifyContent: 'center',
  },
  disabledText: {
    color: '#4ade80',
    fontSize: 14,
    fontWeight: 'bold',
  },
  radioGroup: {
    flexDirection: 'row',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 4,
    overflow: 'hidden',
  },
  radio: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    backgroundColor: '#0a0a0a',
  },
  radioActive: {
    backgroundColor: '#333',
  },
  radioText: {
    color: '#fff',
    fontSize: 14,
  },
  actionRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 10,
  },
  cancelButton: {
    paddingVertical: 14,
    paddingHorizontal: 24,
    marginRight: 16,
    justifyContent: 'center',
  },
  cancelButtonText: {
    color: '#aaa',
    fontWeight: 'bold',
  },
  submitButton: {
    backgroundColor: '#ffcc00',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 4,
    alignItems: 'center',
    minWidth: 150,
  },
  submitButtonText: {
    color: '#0a0a0a',
    fontSize: 14,
    fontWeight: 'bold',
  },
});

