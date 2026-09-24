import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function CreateCRMScreen({ route, navigation }: any) {
  const { type, item } = route.params || {}; // 'Customer' or 'Supplier'
  
  const [formData, setFormData] = useState({
    name: item ? (item.first_name || item.name || '') : '',
    mobile: item ? (item.phone_number || item.mobile || '') : '',
    address: item?.address || '',
    aadhaar_pan: item?.aadhaar_pan || '',
    gst_number: item?.gst_number || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!formData.name || !formData.mobile) {
      Alert.alert('Validation Error', 'Name and Mobile Number are required.');
      return;
    }

    // Must be exactly 10 digits
    if (formData.mobile.length !== 10) {
      Alert.alert('Validation Error', 'Mobile Number must be exactly 10 digits.');
      return;
    }

    try {
      setLoading(true);
      if (type === 'Supplier') {
        const payload = {
          name: formData.name,
          mobile: formData.mobile,
          address: formData.address || undefined,
          gst_number: formData.gst_number || undefined,
        };
        if (item && item.id) {
          await axiosClient.put(`/suppliers/${item.id}`, payload);
        } else {
          await axiosClient.post('/suppliers/', payload);
        }
      } else {
        const payload = {
          first_name: formData.name,
          phone_number: formData.mobile,
          address: formData.address || undefined,
          aadhaar_pan: formData.aadhaar_pan || undefined,
          gst_number: formData.gst_number || undefined
        };
        if (item && item.id) {
          await axiosClient.put(`/customers/${item.id}`, payload);
        } else {
          await axiosClient.post('/customers/', payload);
        }
      }
      
      Alert.alert('Success', `${type} saved successfully!`);
      navigation.goBack();
    } catch (error: any) {
      console.log(`Failed to save ${type}`, error.response?.data || error.message);
      Alert.alert('Error', `Failed to save ${type}. Please check your inputs.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.label}>Name *</Text>
        <TextInput
          style={styles.input}
          placeholder={`Enter ${type} Name`}
          placeholderTextColor="#555"
          value={formData.name}
          onChangeText={(text) => setFormData({ ...formData, name: text })}
        />

        <Text style={styles.label}>Mobile Number *</Text>
        <TextInput
          style={styles.input}
          placeholder="10 digit mobile number"
          placeholderTextColor="#555"
          keyboardType="phone-pad"
          maxLength={10}
          value={formData.mobile}
          onChangeText={(text) => setFormData({ ...formData, mobile: text.replace(/[^0-9]/g, '') })}
        />

        <Text style={styles.label}>Address</Text>
        <TextInput
          style={styles.input}
          placeholder="Enter Address"
          placeholderTextColor="#555"
          multiline
          value={formData.address}
          onChangeText={(text) => setFormData({ ...formData, address: text })}
        />

        {type === 'Customer' && (
          <>
            <Text style={styles.label}>Aadhaar / PAN Card</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter Aadhaar or PAN"
              placeholderTextColor="#555"
              autoCapitalize="characters"
              value={formData.aadhaar_pan}
              onChangeText={(text) => setFormData({ ...formData, aadhaar_pan: text })}
            />
          </>
        )}

        <Text style={styles.label}>GST Number</Text>
        <TextInput
          style={styles.input}
          placeholder="Enter GST Number"
          placeholderTextColor="#555"
          autoCapitalize="characters"
          value={formData.gst_number}
          onChangeText={(text) => setFormData({ ...formData, gst_number: text })}
        />

        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#0a0a0a" />
          ) : (
            <Text style={styles.submitButtonText}>Save {type}</Text>
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
