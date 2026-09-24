import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function CreateInventoryScreen({ navigation }: any) {
  const [formData, setFormData] = useState({
    item_name: '',
    metal: 'Gold', // Matches schema
    category: 'Rings',
    purity: '22K',
    gross_weight: '',
    net_weight: '',
    hsn: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!formData.item_name || !formData.gross_weight || !formData.net_weight || !formData.category) {
      Alert.alert('Validation Error', 'Item Name, Category, Gross Weight and Net Weight are required.');
      return;
    }

    try {
      setLoading(true);
      await axiosClient.post('/stock/', {
        item_name: formData.item_name,
        metal: formData.metal,
        category: formData.category,
        purity: formData.purity || undefined,
        gross_weight: parseFloat(formData.gross_weight),
        net_weight: parseFloat(formData.net_weight),
        stone_weight: parseFloat(formData.gross_weight) - parseFloat(formData.net_weight),
        hsn: formData.hsn || undefined,
        status: 'Available'
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

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.label}>Item Name *</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Gold Ring"
          placeholderTextColor="#555"
          value={formData.item_name}
          onChangeText={(text) => setFormData({ ...formData, item_name: text })}
        />

        <Text style={styles.label}>Metal Type *</Text>
        <View style={styles.row}>
          <TouchableOpacity 
            style={[styles.radio, formData.metal === 'Gold' && styles.radioActive]}
            onPress={() => setFormData({ ...formData, metal: 'Gold' })}
          >
            <Text style={styles.radioText}>Gold</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.radio, formData.metal === 'Silver' && styles.radioActive]}
            onPress={() => setFormData({ ...formData, metal: 'Silver' })}
          >
            <Text style={styles.radioText}>Silver</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.label}>Category *</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Rings, Chains, Coins"
          placeholderTextColor="#555"
          value={formData.category}
          onChangeText={(text) => setFormData({ ...formData, category: text })}
        />

        <Text style={styles.label}>Purity</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. 22K, 18K, 999"
          placeholderTextColor="#555"
          value={formData.purity}
          onChangeText={(text) => setFormData({ ...formData, purity: text })}
        />

        <View style={styles.row}>
          <View style={{ flex: 1, marginRight: 8 }}>
            <Text style={styles.label}>Gross Weight (g) *</Text>
            <TextInput
              style={styles.input}
              placeholder="0.000"
              placeholderTextColor="#555"
              keyboardType="numeric"
              value={formData.gross_weight}
              onChangeText={(text) => setFormData({ ...formData, gross_weight: text })}
            />
          </View>
          <View style={{ flex: 1, marginLeft: 8 }}>
            <Text style={styles.label}>Net Weight (g) *</Text>
            <TextInput
              style={styles.input}
              placeholder="0.000"
              placeholderTextColor="#555"
              keyboardType="numeric"
              value={formData.net_weight}
              onChangeText={(text) => setFormData({ ...formData, net_weight: text })}
            />
          </View>
        </View>

        <Text style={styles.label}>HSN Code</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. 7113"
          placeholderTextColor="#555"
          keyboardType="numeric"
          value={formData.hsn}
          onChangeText={(text) => setFormData({ ...formData, hsn: text })}
        />

        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#0a0a0a" />
          ) : (
            <Text style={styles.submitButtonText}>Add to Inventory</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 16,
  },
  card: {
    backgroundColor: '#141414',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 40,
  },
  label: {
    color: '#888',
    fontSize: 14,
    marginBottom: 8,
    fontWeight: 'bold',
  },
  input: {
    backgroundColor: '#1a1a1a',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    padding: 12,
    color: '#fff',
    fontSize: 16,
    marginBottom: 16,
  },
  row: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  radio: {
    flex: 1,
    padding: 12,
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    alignItems: 'center',
    marginRight: 8,
  },
  radioActive: {
    backgroundColor: '#333',
    borderColor: '#d4af37',
  },
  radioText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  submitButton: {
    backgroundColor: '#d4af37',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  submitButtonText: {
    color: '#0a0a0a',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
