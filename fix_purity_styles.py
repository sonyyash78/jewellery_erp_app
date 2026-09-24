import re

with open('src/components/MobileMetalCalculator.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace(
    "purityBtnActive: { borderColor: '#d4af37', backgroundColor: 'rgba(212?75,55,0.1)' },", 
    "purityBtnActive: { borderColor: '#d4af37', backgroundColor: 'rgba(212, 175, 55, 0.1)' },\n  purityBtnActiveSilver: { borderColor: '#e5e7eb', backgroundColor: 'rgba(229, 231, 235, 0.1)' },"
)

with open('src/components/MobileMetalCalculator.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
