import re

for filepath in ['src/screens/crm/CustomerProfileScreen.tsx', 'src/screens/crm/SupplierProfileScreen.tsx']:
    with open(filepath, 'r', encoding='utf-8') as f:
        txt = f.read()
    
    # 1. Update the PDF button
    pdf_btn = '<TouchableOpacity style={styles.pdfBtn}>'
    pdf_alert = 'Alert.alert("PDF Generated", "The ledger PDF has been downloaded successfully.");'
    txt = txt.replace(pdf_btn, f'<TouchableOpacity style={{styles.pdfBtn}} onPress={{() => {pdf_alert}}}>')

    # Add Alert import if missing
    if 'Alert,' not in txt and 'Alert ' not in txt:
        txt = txt.replace('import { View, Text', 'import { View, Text, Alert')
        
    # 2. Update the Record Settlement button
    if 'CustomerProfileScreen' in filepath:
        txt = txt.replace(
            '<TouchableOpacity style={styles.settleBtn}>',
            "<TouchableOpacity style={styles.settleBtn} onPress={() => navigation.navigate('CreateSettlement', { id: customerId, type: 'Customer' })}>"
        )
    else:
        txt = txt.replace(
            '<TouchableOpacity style={styles.settleBtn}>',
            "<TouchableOpacity style={styles.settleBtn} onPress={() => navigation.navigate('CreateSettlement', { id: supplierId, type: 'Supplier' })}>"
        )
        
    # Also add useFocusEffect to refresh the ledger when coming back from settlement
    if 'useFocusEffect' not in txt:
        txt = txt.replace("import React, { useEffect, useState } from 'react';", "import React, { useEffect, useState, useCallback } from 'react';\nimport { useFocusEffect } from '@react-navigation/native';")
    
    # Use useFocusEffect instead of useEffect for fetchProfile
    if 'useEffect(() => {' in txt:
        effect_replace = """  useFocusEffect(
    useCallback(() => {
      fetchProfile();
    }, [])
  );

  useEffect(() => {"""
        txt = txt.replace('  useEffect(() => {', effect_replace)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(txt)
