import re

with open('src/components/MobileMetalCalculator.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# 1. Add renderSilverPurity
silver_purity = """  const renderSilverPurity = () => {
    const opts = [
      { l: 'Fine', t: '99.9', r: liveRates?.silver || 90000 },
      { l: 'Sterling', t: '92.5', r: (liveRates?.silver || 90000) * 0.925 },
      { l: 'Custom', t: '65.0', r: (liveRates?.silver || 90000) * 0.65 },
    ];
    return (
      <View style={styles.purityRow}>
        {opts.map(o => (
          <TouchableOpacity 
            key={o.l} 
            style={[styles.purityBtn, sCategory === o.l && styles.purityBtnActiveSilver]}
            onPress={() => { setSCategory(o.l); setSTouch(o.t); setSRate(o.r.toString()); }}
          >
            <Text style={[styles.purityText, sCategory === o.l && styles.purityTextActiveSilver]}>{o.l} ({o.t})</Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };"""

txt = txt.replace('  const renderGoldPurity = () => {', silver_purity + '\n\n  const renderGoldPurity = () => {')

# 2. Add to JSX
jsx = """      {metal === 'Gold' && (
        <View style={{ marginBottom: 12 }}>
          <Text style={styles.label}>Gold Purity</Text>
          {renderGoldPurity()}
        </View>
      )}"""
jsx_silver = """      {metal === 'Gold' && (
        <View style={{ marginBottom: 12 }}>
          <Text style={styles.label}>Gold Purity</Text>
          {renderGoldPurity()}
        </View>
      )}
      
      {metal === 'Silver' && (
        <View style={{ marginBottom: 12 }}>
          <Text style={styles.label}>Silver Purity</Text>
          {renderSilverPurity()}
        </View>
      )}"""

txt = txt.replace(jsx, jsx_silver)

# 3. Add Silver styles
style_replace = """  purityBtnActive: { borderColor: '#d4af37', backgroundColor: 'rgba(212, 175, 55, 0.1)' },
  purityBtnActiveSilver: { borderColor: '#e5e7eb', backgroundColor: 'rgba(229, 231, 235, 0.1)' },
  purityText: { color: '#888', fontSize: 11, fontWeight: 'bold' },
  purityTextActive: { color: '#d4af37' },
  purityTextActiveSilver: { color: '#e5e7eb' },"""

txt = re.sub(
    r"  purityBtnActive: \{ borderColor: '#d4af37', backgroundColor: 'rgba\(212\?75,55,0\.1\)' \},\n  purityText: \{ color: '#888', fontSize: 11, fontWeight: 'bold' \},\n  purityTextActive: \{ color: '#d4af37' \},",
    style_replace,
    txt
)

# wait, the regex above had a corrupted `rgba(212?75,55,0.1)` because of powershell.
# Let's just use string replace carefully
txt = txt.replace("purityBtnActive: { borderColor: '#d4af37', backgroundColor: 'rgba(212?75,55,0.1)' },", "purityBtnActive: { borderColor: '#d4af37', backgroundColor: 'rgba(212, 175, 55, 0.1)' },\n  purityBtnActiveSilver: { borderColor: '#e5e7eb', backgroundColor: 'rgba(229, 231, 235, 0.1)' },")
txt = txt.replace("purityTextActive: { color: '#d4af37' },", "purityTextActive: { color: '#d4af37' },\n  purityTextActiveSilver: { color: '#e5e7eb' },")


with open('src/components/MobileMetalCalculator.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
