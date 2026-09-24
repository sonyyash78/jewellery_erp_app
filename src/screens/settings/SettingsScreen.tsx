import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { axiosClient } from '../../api/axiosClient';

const SETTING_GROUPS = [
  {
    title: 'Store Information',
    keys: [
      { key: 'store_name', label: 'Store / Business Name' },
      { key: 'store_address', label: 'Store Address' },
      { key: 'store_phone', label: 'Store Phone' },
      { key: 'store_email', label: 'Store Email' },
      { key: 'store_gstin', label: 'GSTIN' },
    ]
  },
  {
    title: 'Bill QR Code & Payment Info',
    keys: [
      { key: 'upi_id', label: 'UPI ID for QR Code (e.g. 9876543210@upi)' },
      { key: 'upi_name', label: 'UPI Payee Name (e.g. Saideep Jewellers)' },
      { key: 'qr_image_url', label: 'Custom QR Code Image URL (Optional)' },
    ]
  },
  {
    title: 'Print & Invoice Terms',
    keys: [
      { key: 'print_hallmark', label: 'Print Hallmark Text' },
      { key: 'print_wastage', label: 'Print Wastage Text' },
      { key: 'print_making_charges', label: 'Print Making Charges Text' },
      { key: 'print_remarks', label: 'Print Remarks' },
    ]
  }
];

export default function SettingsScreen() {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await axiosClient.get('/settings/');
      setSettings(res.data || {});
    } catch (error) {
      console.log('Failed to fetch settings', error);
      Alert.alert('Error', 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const payload = Object.entries(settings).map(([key, value]) => ({ key, value }));
      await axiosClient.post('/settings/', payload);
      Alert.alert('Success', 'Settings & QR Code configuration saved successfully!');
    } catch (error) {
      console.log('Failed to save settings', error);
      Alert.alert('Error', 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (key: string, value: string) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#d4af37" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {SETTING_GROUPS.map((group, gIdx) => (
        <View key={gIdx} style={styles.card}>
          <Text style={styles.headerTitle}>{group.title}</Text>
          
          {group.keys.map((item) => (
            <View key={item.key} style={styles.inputGroup}>
              <Text style={styles.label}>{item.label}</Text>
              <TextInput
                style={styles.input}
                value={settings[item.key] || ''}
                onChangeText={(text) => handleChange(item.key, text)}
                placeholder={`Enter ${item.label}`}
                placeholderTextColor="#555"
                multiline={item.key.includes('address') || item.key.includes('print')}
                autoCapitalize={item.key === 'upi_id' ? 'none' : 'sentences'}
              />
            </View>
          ))}
        </View>
      ))}

      <TouchableOpacity 
        style={styles.saveButton} 
        onPress={handleSave}
        disabled={saving}
      >
        {saving ? (
          <ActivityIndicator color="#0a0a0a" />
        ) : (
          <Text style={styles.saveButtonText}>Save Settings & QR</Text>
        )}
      </TouchableOpacity>
      
      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 16,
  },
  center: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    backgroundColor: '#141414',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 16,
  },
  headerTitle: {
    color: '#d4af37',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#262626',
    paddingBottom: 8,
  },
  inputGroup: {
    marginBottom: 14,
  },
  label: {
    color: '#aaa',
    fontSize: 13,
    marginBottom: 6,
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#1a1a1a',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    padding: 12,
    color: '#fff',
    fontSize: 15,
  },
  saveButton: {
    backgroundColor: '#d4af37',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 4,
  },
  saveButtonText: {
    color: '#0a0a0a',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
