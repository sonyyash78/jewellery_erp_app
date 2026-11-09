import os

p = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\MetalCalculator.tsx"
with open(p, "r", encoding="utf-8") as f:
    text = f.read()

# Replace corrupted characters
text = text.replace("dY Gold", "🟡 Gold")
text = text.replace("dY^ Silver", "⚪ Silver")
text = text.replace("dY'Z Diamond", "💎 Diamond")
text = text.replace(",1", "₹")
text = text.replace("?\"", "—")

# Add 100% Bar preset in Silver Purity if not present
if "Bar 100% (71069120)" not in text:
    silver_purity_target = """                  {[
                    { label: 'Fine (99.9)', val: 'Fine', tanch: 99.9 },"""
    silver_purity_repl = """                  {[
                    { label: '🥈 Bar 100% (71069120)', val: '100% Bar', tanch: 100.0 },
                    { label: 'Fine (99.9)', val: 'Fine', tanch: 99.9 },"""
    text = text.replace(silver_purity_target, silver_purity_repl)

# Add 24K Bar preset in Gold Purity if not present
if "Bar 99.9% (71081200)" not in text:
    gold_purity_target = """                  {[
                    { label: '24K (99.9)', val: '24K', rate: liveRates.gold24k || 0, touch: 99.9 },"""
    gold_purity_repl = """                  {[
                    { label: '🥇 Bar 99.9% (71081200)', val: '24K Bar', rate: liveRates.gold24k || 79000, touch: 99.9 },
                    { label: '24K (99.9)', val: '24K', rate: liveRates.gold24k || 0, touch: 99.9 },"""
    text = text.replace(gold_purity_target, gold_purity_repl)

with open(p, "w", encoding="utf-8") as f:
    f.write(text)

print("Cleaned up MetalCalculator.tsx with proper symbols and bullion presets")
