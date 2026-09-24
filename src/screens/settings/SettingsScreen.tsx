import React, { useEffect, useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  TextInput, 
  TouchableOpacity, 
  ActivityIndicator, 
  Alert,
  Image
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { axiosClient } from '../../api/axiosClient';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';

export default function SettingsScreen() {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [downloadingSingleExcel, setDownloadingSingleExcel] = useState(false);
  const [downloadingExcel, setDownloadingExcel] = useState(false);
  const [downloadingSql, setDownloadingSql] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await axiosClient.get('/settings/');
      const data = res.data || {};
      
      // Auto-populate legacy store_* keys into business_* keys if needed
      if (!data.business_name && data.store_name) data.business_name = data.store_name;
      if (!data.phone && data.store_phone) data.phone = data.store_phone;
      if (!data.email && data.store_email) data.email = data.store_email;
      if (!data.gstin && data.store_gstin) data.gstin = data.store_gstin;
      if (!data.address && data.store_address) data.address = data.store_address;

      setSettings(data);
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
      Alert.alert('Success', 'Settings & Payment QR Code configuration saved successfully!');
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

  const handleDownloadSingleMasterExcel = async () => {
    try {
      setDownloadingSingleExcel(true);
      const baseUrl = axiosClient.defaults.baseURL || '';
      const backupUrl = `${baseUrl.replace(/\/api\/v1\/?$/, '')}/api/v1/backup/all-tables-excel`;
      const timestamp = new Date().toISOString().slice(0, 10);
      const localFileUri = `${FileSystem.documentDirectory}jewellery_erp_all_tables_${timestamp}.xlsx`;

      const downloadRes = await FileSystem.downloadAsync(backupUrl, localFileUri, {
        headers: axiosClient.defaults.headers.common as Record<string, string>
      });

      if (downloadRes.status === 200) {
        if (await Sharing.isAvailableAsync()) {
          await Sharing.shareAsync(localFileUri, {
            mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            dialogTitle: 'Share Complete Database (Master Excel .xlsx)',
            UTI: 'com.microsoft.excel.xlsx'
          });
        } else {
          Alert.alert('Backup Saved', `Master Excel workbook saved to:\n${localFileUri}`);
        }
      } else {
        Alert.alert('Error', `Download failed with status ${downloadRes.status}`);
      }
    } catch (error) {
      console.log('Master Excel backup error', error);
      Alert.alert('Error', 'Failed to download Master Excel workbook.');
    } finally {
      setDownloadingSingleExcel(false);
    }
  };

  const handleDownloadExcelBackup = async () => {
    try {
      setDownloadingExcel(true);
      const baseUrl = axiosClient.defaults.baseURL || '';
      const backupUrl = `${baseUrl.replace(/\/api\/v1\/?$/, '')}/api/v1/backup/excel-download`;
      const timestamp = new Date().toISOString().slice(0, 10);
      const localFileUri = `${FileSystem.documentDirectory}jewellery_erp_excel_backup_${timestamp}.zip`;

      const downloadRes = await FileSystem.downloadAsync(backupUrl, localFileUri, {
        headers: axiosClient.defaults.headers.common as Record<string, string>
      });

      if (downloadRes.status === 200) {
        if (await Sharing.isAvailableAsync()) {
          await Sharing.shareAsync(localFileUri, {
            mimeType: 'application/zip',
            dialogTitle: 'Share Database Data (Excel ZIP)'
          });
        } else {
          Alert.alert('Backup Saved', `Excel data backup saved to:\n${localFileUri}`);
        }
      } else {
        Alert.alert('Error', `Download failed with status ${downloadRes.status}`);
      }
    } catch (error) {
      console.log('Excel backup error', error);
      Alert.alert('Error', 'Failed to download Database Excel backup.');
    } finally {
      setDownloadingExcel(false);
    }
  };

  const handleDownloadSqlBackup = async () => {
    try {
      setDownloadingSql(true);
      const baseUrl = axiosClient.defaults.baseURL || '';
      const backupUrl = `${baseUrl.replace(/\/api\/v1\/?$/, '')}/api/v1/backup/download`;
      const timestamp = new Date().toISOString().slice(0, 10);
      const localFileUri = `${FileSystem.documentDirectory}jewellery_erp_backup_${timestamp}.sql`;

      const downloadRes = await FileSystem.downloadAsync(backupUrl, localFileUri, {
        headers: axiosClient.defaults.headers.common as Record<string, string>
      });

      if (downloadRes.status === 200) {
        if (await Sharing.isAvailableAsync()) {
          await Sharing.shareAsync(localFileUri, {
            mimeType: 'application/sql',
            dialogTitle: 'Share Full SQL Database Backup'
          });
        } else {
          Alert.alert('Backup Saved', `Database SQL backup saved to:\n${localFileUri}`);
        }
      } else {
        Alert.alert('Error', `Download failed with status ${downloadRes.status}`);
      }
    } catch (error) {
      console.log('SQL backup error', error);
      Alert.alert('Error', 'Failed to download SQL backup.');
    } finally {
      setDownloadingSql(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#d4af37" />
        <Text style={{ color: '#888', marginTop: 12, fontSize: 13 }}>Loading settings...</Text>
      </View>
    );
  }

  const currentUpiId = settings['upi_id'] || 'saideepjewellers@upi';
  const currentUpiName = settings['upi_name'] || settings['business_name'] || 'SAIDEEP JEWELLERS';
  const previewQrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent('upi://pay?pa=' + currentUpiId + '&pn=' + encodeURIComponent(currentUpiName) + '&cu=INR')}`;

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 60 }}>
      
      {/* 1. Business Profile */}
      <View style={styles.card}>
        <View style={styles.headerRow}>
          <Ionicons name="business-outline" size={20} color="#d4af37" />
          <Text style={styles.headerTitle}>Business Profile</Text>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Business / Store Name</Text>
          <TextInput
            style={styles.input}
            value={settings['business_name'] || ''}
            onChangeText={(text) => handleChange('business_name', text)}
            placeholder="e.g. SAIDEEP JEWELLERS"
            placeholderTextColor="#555"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Tagline (Subtitle)</Text>
          <TextInput
            style={styles.input}
            value={settings['tagline'] || ''}
            onChangeText={(text) => handleChange('tagline', text)}
            placeholder="e.g. Trust. Purity. Elegance."
            placeholderTextColor="#555"
          />
        </View>

        <View style={styles.rowInputs}>
          <View style={[styles.inputGroup, { flex: 1 }]}>
            <Text style={styles.label}>Phone Number</Text>
            <TextInput
              style={styles.input}
              value={settings['phone'] || ''}
              onChangeText={(text) => handleChange('phone', text)}
              placeholder="e.g. 9460820878"
              placeholderTextColor="#555"
              keyboardType="phone-pad"
            />
          </View>

          <View style={[styles.inputGroup, { flex: 1 }]}>
            <Text style={styles.label}>Email Address</Text>
            <TextInput
              style={styles.input}
              value={settings['email'] || ''}
              onChangeText={(text) => handleChange('email', text)}
              placeholder="e.g. shop@gmail.com"
              placeholderTextColor="#555"
              keyboardType="email-address"
              autoCapitalize="none"
            />
          </View>
        </View>

        <View style={styles.rowInputs}>
          <View style={[styles.inputGroup, { flex: 1 }]}>
            <Text style={styles.label}>GSTIN Number</Text>
            <TextInput
              style={styles.input}
              value={settings['gstin'] || ''}
              onChangeText={(text) => handleChange('gstin', text)}
              placeholder="GSTIN"
              placeholderTextColor="#555"
              autoCapitalize="characters"
            />
          </View>

          <View style={[styles.inputGroup, { flex: 1 }]}>
            <Text style={styles.label}>PAN Number</Text>
            <TextInput
              style={styles.input}
              value={settings['pan'] || ''}
              onChangeText={(text) => handleChange('pan', text)}
              placeholder="PAN Number"
              placeholderTextColor="#555"
              autoCapitalize="characters"
            />
          </View>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Store Address</Text>
          <TextInput
            style={[styles.input, { height: 70, textAlignVertical: 'top' }]}
            value={settings['address'] || ''}
            onChangeText={(text) => handleChange('address', text)}
            placeholder="Enter physical address"
            placeholderTextColor="#555"
            multiline
          />
        </View>
      </View>

      {/* 2. UPI & Online Payment QR Settings */}
      <View style={[styles.card, { borderColor: '#d4af37' }]}>
        <View style={styles.headerRow}>
          <Ionicons name="qr-code-outline" size={20} color="#d4af37" />
          <Text style={styles.headerTitle}>UPI & Bill Payment QR Code</Text>
        </View>
        <Text style={styles.sectionSubtitle}>
          This QR code is generated dynamically on Tax Invoices & Bills so your customers can scan and pay directly from Google Pay, PhonePe, Paytm, or BHIM.
        </Text>

        <View style={styles.qrPreviewContainer}>
          <View style={styles.qrImageWrapper}>
            <Image 
              source={{ uri: previewQrUrl }} 
              style={styles.qrImage}
              resizeMode="contain"
            />
            <View style={styles.scanBadge}>
              <Text style={styles.scanBadgeText}>SCAN TO PAY</Text>
            </View>
          </View>

          <View style={styles.qrInfoWrapper}>
            <Text style={styles.qrInfoLabel}>UPI Payee:</Text>
            <Text style={styles.qrInfoValue}>{currentUpiName}</Text>
            <Text style={[styles.qrInfoLabel, { marginTop: 6 }]}>UPI ID (VPA):</Text>
            <Text style={[styles.qrInfoValue, { fontFamily: 'monospace', color: '#22c55e' }]}>{currentUpiId}</Text>
            <Text style={styles.qrNote}>Dynamic bill amount & invoice reference are auto-encoded on invoices.</Text>
          </View>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>UPI ID (VPA)</Text>
          <TextInput
            style={[styles.input, { fontFamily: 'monospace' }]}
            value={settings['upi_id'] || ''}
            onChangeText={(text) => handleChange('upi_id', text)}
            placeholder="e.g. 9460820878@upi or saideepjewellers@okhdfcbank"
            placeholderTextColor="#555"
            autoCapitalize="none"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>UPI Payee / Shop Name</Text>
          <TextInput
            style={styles.input}
            value={settings['upi_name'] || ''}
            onChangeText={(text) => handleChange('upi_name', text)}
            placeholder="e.g. SAIDEEP JEWELLERS"
            placeholderTextColor="#555"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Bank Name (Optional)</Text>
          <TextInput
            style={styles.input}
            value={settings['bank_name'] || ''}
            onChangeText={(text) => handleChange('bank_name', text)}
            placeholder="e.g. HDFC Bank / State Bank of India"
            placeholderTextColor="#555"
          />
        </View>

        <View style={styles.rowInputs}>
          <View style={[styles.inputGroup, { flex: 1.2 }]}>
            <Text style={styles.label}>Bank Account No (Optional)</Text>
            <TextInput
              style={[styles.input, { fontFamily: 'monospace' }]}
              value={settings['bank_account_no'] || ''}
              onChangeText={(text) => handleChange('bank_account_no', text)}
              placeholder="Account Number"
              placeholderTextColor="#555"
              keyboardType="numeric"
            />
          </View>

          <View style={[styles.inputGroup, { flex: 0.8 }]}>
            <Text style={styles.label}>IFSC Code (Optional)</Text>
            <TextInput
              style={[styles.input, { fontFamily: 'monospace' }]}
              value={settings['bank_ifsc'] || ''}
              onChangeText={(text) => handleChange('bank_ifsc', text)}
              placeholder="IFSC Code"
              placeholderTextColor="#555"
              autoCapitalize="characters"
            />
          </View>
        </View>
      </View>

      {/* 3. Invoice Print Settings */}
      <View style={styles.card}>
        <View style={styles.headerRow}>
          <Ionicons name="receipt-outline" size={20} color="#d4af37" />
          <Text style={styles.headerTitle}>Invoice Print Settings (Other Details)</Text>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Print Hallmark</Text>
          <TextInput
            style={[styles.input, { height: 60, textAlignVertical: 'top' }]}
            value={settings['print_hallmark'] || ''}
            onChangeText={(text) => handleChange('print_hallmark', text)}
            placeholder="BIS 916 (Gold)&#10;BIS 925 (Silver)"
            placeholderTextColor="#555"
            multiline
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Print Wastage</Text>
          <TextInput
            style={styles.input}
            value={settings['print_wastage'] || ''}
            onChangeText={(text) => handleChange('print_wastage', text)}
            placeholder="0.00%"
            placeholderTextColor="#555"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Print Making Charges</Text>
          <TextInput
            style={[styles.input, { height: 60, textAlignVertical: 'top' }]}
            value={settings['print_making_charges'] || ''}
            onChangeText={(text) => handleChange('print_making_charges', text)}
            placeholder="Gold ₹ 1,000.00/gm&#10;Silver ₹ 20.00/gm"
            placeholderTextColor="#555"
            multiline
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Print Remarks</Text>
          <TextInput
            style={[styles.input, { height: 60, textAlignVertical: 'top' }]}
            value={settings['print_remarks'] || ''}
            onChangeText={(text) => handleChange('print_remarks', text)}
            placeholder="Subject to realization of cheque."
            placeholderTextColor="#555"
            multiline
          />
        </View>
      </View>

      {/* 4. Save Settings Button */}
      <TouchableOpacity 
        style={styles.saveButton} 
        onPress={handleSave}
        disabled={saving}
      >
        {saving ? (
          <ActivityIndicator color="#0a0a0a" />
        ) : (
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
            <Ionicons name="save-outline" size={20} color="#0a0a0a" />
            <Text style={styles.saveButtonText}>Save Settings & Payment QR</Text>
          </View>
        )}
      </TouchableOpacity>

      {/* 5. Database & Excel Backup Card */}
      <View style={[styles.card, { marginTop: 24, borderColor: '#334155' }]}>
        <View style={styles.headerRow}>
          <Ionicons name="server-outline" size={20} color="#38bdf8" />
          <Text style={[styles.headerTitle, { color: '#38bdf8' }]}>Database & Excel Data Export</Text>
        </View>
        <Text style={styles.sectionSubtitle}>
          Download complete database records in Excel format (ZIP with individual table sheets) or full SQL backups directly to your mobile device.
        </Text>

        <View style={{ gap: 12, marginTop: 6 }}>
          <TouchableOpacity 
            style={[styles.backupBtn, { borderColor: 'rgba(16, 185, 129, 0.5)', backgroundColor: 'rgba(16, 185, 129, 0.15)' }]}
            onPress={handleDownloadSingleMasterExcel}
            disabled={downloadingSingleExcel}
          >
            {downloadingSingleExcel ? (
              <ActivityIndicator color="#10b981" />
            ) : (
              <View style={styles.backupBtnContent}>
                <Ionicons name="document-text-outline" size={20} color="#10b981" />
                <View style={{ flex: 1 }}>
                  <Text style={[styles.backupBtnTitle, { color: '#10b981' }]}>Download All Tables (Master Excel .xlsx)</Text>
                  <Text style={styles.backupBtnSub}>Single Excel workbook with all tables as separate sheet tabs (Best for Mobile)</Text>
                </View>
              </View>
            )}
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.backupBtn, { borderColor: 'rgba(34, 197, 94, 0.4)', backgroundColor: 'rgba(34, 197, 94, 0.12)' }]}
            onPress={handleDownloadExcelBackup}
            disabled={downloadingExcel}
          >
            {downloadingExcel ? (
              <ActivityIndicator color="#22c55e" />
            ) : (
              <View style={styles.backupBtnContent}>
                <Ionicons name="grid-outline" size={18} color="#22c55e" />
                <View style={{ flex: 1 }}>
                  <Text style={[styles.backupBtnTitle, { color: '#22c55e' }]}>Download Database Data (Excel ZIP)</Text>
                  <Text style={styles.backupBtnSub}>Export all sales, purchases, inventory & customer tables as individual Excel files</Text>
                </View>
              </View>
            )}
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.backupBtn, { borderColor: 'rgba(212, 175, 55, 0.4)', backgroundColor: 'rgba(212, 175, 55, 0.12)' }]}
            onPress={handleDownloadSqlBackup}
            disabled={downloadingSql}
          >
            {downloadingSql ? (
              <ActivityIndicator color="#d4af37" />
            ) : (
              <View style={styles.backupBtnContent}>
                <Ionicons name="cloud-download-outline" size={18} color="#d4af37" />
                <View style={{ flex: 1 }}>
                  <Text style={[styles.backupBtnTitle, { color: '#d4af37' }]}>Download Full Backup (.sql)</Text>
                  <Text style={styles.backupBtnSub}>Complete database snapshot for full system restoration</Text>
                </View>
              </View>
            )}
          </TouchableOpacity>
        </View>
      </View>

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 14,
  },
  center: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    backgroundColor: '#141414',
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: '#262626',
    marginBottom: 16,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#262626',
    paddingBottom: 8,
  },
  headerTitle: {
    color: '#d4af37',
    fontSize: 16,
    fontWeight: 'bold',
  },
  sectionSubtitle: {
    color: '#888',
    fontSize: 12,
    lineHeight: 17,
    marginBottom: 14,
  },
  rowInputs: {
    flexDirection: 'row',
    gap: 10,
  },
  inputGroup: {
    marginBottom: 12,
  },
  label: {
    color: '#999',
    fontSize: 12,
    marginBottom: 5,
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#1a1a1a',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: '#fff',
    fontSize: 14,
  },
  qrPreviewContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#333',
    marginBottom: 14,
  },
  qrImageWrapper: {
    backgroundColor: '#fff',
    padding: 6,
    borderRadius: 8,
    alignItems: 'center',
  },
  qrImage: {
    width: 80,
    height: 80,
  },
  scanBadge: {
    backgroundColor: '#0B132B',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 3,
    marginTop: 4,
  },
  scanBadgeText: {
    color: '#d4af37',
    fontSize: 8,
    fontWeight: 'bold',
  },
  qrInfoWrapper: {
    flex: 1,
  },
  qrInfoLabel: {
    color: '#777',
    fontSize: 11,
    fontWeight: '600',
  },
  qrInfoValue: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
  },
  qrNote: {
    color: '#666',
    fontSize: 10,
    marginTop: 6,
    fontStyle: 'italic',
  },
  saveButton: {
    backgroundColor: '#d4af37',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 6,
  },
  saveButtonText: {
    color: '#0a0a0a',
    fontSize: 15,
    fontWeight: 'bold',
  },
  backupBtn: {
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
  },
  backupBtnContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  backupBtnTitle: {
    fontSize: 13,
    fontWeight: 'bold',
  },
  backupBtnSub: {
    color: '#888',
    fontSize: 11,
    marginTop: 2,
  },
});
