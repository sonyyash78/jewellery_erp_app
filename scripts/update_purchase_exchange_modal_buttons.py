import os

repo_root = r"C:\Users\YASH SONI\Desktop\jeweller-app"

for file_path in [
    os.path.join(repo_root, "frontend", "src", "pages", "purchase", "PurchaseCheckoutModal.tsx"),
    os.path.join(repo_root, "frontend", "src", "pages", "exchange", "ExchangeCheckoutModal.tsx")
]:
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Add data-nav-button
    code = code.replace('<button onClick={onClose} className="py-2.5 sm:py-3 px-4 border',
                        '<button data-nav-button="true" onClick={onClose} className="py-2.5 sm:py-3 px-4 border')
    code = code.replace('<button onClick={() => handleGenerate(false)} disabled={loading',
                        '<button data-nav-button="true" onClick={() => handleGenerate(false)} disabled={loading')
    code = code.replace('<button onClick={() => handleGenerate(true)} disabled={loading',
                        '<button data-nav-button="true" onClick={() => handleGenerate(true)} disabled={loading')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Updated buttons in", os.path.basename(file_path))
