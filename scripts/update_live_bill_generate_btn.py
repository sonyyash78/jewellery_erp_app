p = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\LiveBillSummary.tsx'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        {/* Generate Bill Button */}
        <button
          disabled={cart.length === 0}
          onClick={handleGenerate}
          className="bg-primary hover:bg-primary-dark text-black font-bold py-2.5 rounded w-full flex items-center justify-center gap-2 transition-colors disabled:opacity-50 text-sm shadow-md"
        >
          <Calculator size={16} />
          GENERATE BILL (F12)
        </button>'''

replacement = '''        {/* Generate Bill Button */}
        <button
          id="btn-generate-bill"
          data-nav-button="true"
          disabled={cart.length === 0}
          onClick={handleGenerate}
          className="bg-primary hover:bg-primary-dark text-black font-bold py-2.5 rounded w-full flex items-center justify-center gap-2 transition-colors disabled:opacity-50 text-sm shadow-md focus:ring-2 focus:ring-offset-2 focus:ring-primary"
        >
          <Calculator size={16} />
          GENERATE BILL (F12 / Enter)
        </button>'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully updated LiveBillSummary.tsx!")
else:
    print("Could not match target in LiveBillSummary.tsx")
