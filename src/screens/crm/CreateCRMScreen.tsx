import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

export default function CreateCRMScreen({ route, navigation }: any) {
  const { type } = route.params; // 'Customer' or 'Supplier'
  
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    address: '',
    pan_card: '',
    aadhar_card: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!formData.name || !formData.phone_number) {
      Alert.alert('Validation Error', 'Name and Phone Number are required.');
      return;
    }

    try {
      setLoading(true);
      const endpoint = type === 'Supplier' ? '/suppliers/' : '/customers/';
      await axiosClient.post(endpoint, formData);
      Alert.alert('Success', `${type} created successfully!`);
      navigation.goBack();
    } catch (error) {
      console.log(`Failed to create ${type}`, error);
      Alert.alert('Error', `Failed to create ${type}`);
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

        <Text style={styles.label}>Phone Number *</Text>
        <TextInput
          style={styles.input}
          placeholder="Enter Phone Number"
          placeholderTextColor="#555"
          keyboardType="phone-pad"
          value={formData.phone_number}
          onChangeText={(text) => setFormData({ ...formData, phone_number: text })}
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

        <Text style={styles.label}>PAN Card</Text>
        <TextInput
          style={styles.input}
          placeholder="Enter PAN Number"
          placeholderTextColor="#555"
          autoCapitalize="characters"
          value={formData.pan_card}
          onChangeText={(text) => setFormData({ ...formData, pan_card: text })}
        />

        <Text style={styles.label}>Aadhar Card</Text>
        <TextInput
          style={styles.input}
          placeholder="Enter Aadhar Number"
          placeholderTextColor="#555"
          keyboardType="number-pad"
          value={formData.aadhar_card}
          onChangeText={(text) => setFormData({ ...formData, aadhar_card: text })}
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
