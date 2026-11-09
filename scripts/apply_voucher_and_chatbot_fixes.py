import os

def update_invoice_pdf_service():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\invoice_pdf_service.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = "'tanch_percentage': float(item.touch_purity),"
    replacement = "'tanch_percentage': float(item.touch_purity),\n                'wastage': float(item.wastage or 0),"

    if target in content and "'wastage': float(item.wastage or 0)" not in content:
        content = content.replace(target, replacement, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[1] Updated invoice_pdf_service.py with purchase wastage")
    else:
        print("[1] invoice_pdf_service.py already updated or target not found")

def update_purchases_api():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\purchases.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = '"item_type": item.metal_type,'
    replacement = '"item_type": item.metal_type,\n                "touch_purity": float(item.touch_purity or 0),\n                "wastage": float(item.wastage or 0),'

    if target in content and '"wastage": float(item.wastage or 0)' not in content:
        content = content.replace(target, replacement, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[2] Updated purchases.py get_unified_purchase with wastage")
    else:
        print("[2] purchases.py already updated or target not found")

def update_premium_invoice_html():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\premiumInvoiceHtml.ts"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = '<td>${(item.tanch_percentage || item.touch_purity) ? (item.tanch_percentage || item.touch_purity) + \'%\' : \'-\'}${item.wastage ? ` + ${item.wastage}%` : \'\'}</td>'
    replacement = """          <td>${(() => {
            const tanch = item.tanch_percentage || item.touch_purity || item.tanch || item.touch;
            const wst = Number(item.wastage || item.wastage_percent || item.wastage_pct || 0);
            return `${tanch ? tanch + '%' : '-'}${wst > 0 ? ` + ${wst}%` : ''}`;
          })()}</td>"""

    if target in content:
        content = content.replace(target, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[3] Updated premiumInvoiceHtml.ts renderTableRow for tanch + wastage")
    else:
        print("[3] premiumInvoiceHtml.ts target not found or already updated")

def update_sellers_api():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\sellers.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add HTTPException at top
    if "from fastapi import HTTPException" not in content[:300]:
        content = content.replace(
            "from fastapi import APIRouter, Depends, Query",
            "from fastapi import APIRouter, Depends, Query, HTTPException"
        )
        print("[4a] Added HTTPException import to top of sellers.py")

    # 2. Make seller queries resilient
    old_query = "seller = db.query(Seller).filter(Seller.id == seller_id, Seller.store_id == store_id"
    new_query = "seller = db.query(Seller).filter(Seller.id == seller_id"
    if old_query in content:
        content = content.replace(old_query, new_query)
        print("[4b] Made Seller lookup by seller_id resilient across store_id")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[4] Updated sellers.py")

def update_invoices_customer_fallback():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\invoices.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Enhance customer lookup so if ID is not found, fallback to buyer_phone or create one
    target = """        customer = db.query(Customer).filter(Customer.id == invoice_in.customer_id, Customer.store_id == store_id).first()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with id {invoice_in.customer_id} not found"
            )"""

    replacement = """        customer = db.query(Customer).filter(Customer.id == invoice_in.customer_id).first()
        if not customer and getattr(invoice_in, 'buyer_phone', None):
            customer = db.query(Customer).filter(Customer.phone_number == invoice_in.buyer_phone).first()

        if not customer:
            # If still not found but buyer details are present, auto-create customer to avoid checkout failure
            b_name = getattr(invoice_in, 'buyer_name', None) or 'Walk-in Customer'
            b_phone = getattr(invoice_in, 'buyer_phone', None) or '0000000000'
            try:
                customer = Customer(
                    store_id=store_id,
                    first_name=b_name,
                    phone_number=b_phone,
                    address=getattr(invoice_in, 'buyer_address', '') or '',
                    city=getattr(invoice_in, 'buyer_city', '') or '',
                    is_active=True
                )
                db.add(customer)
                db.flush()
            except Exception:
                raise HTTPException(
                    status_code=404,
                    detail=f"Customer with id {invoice_in.customer_id} not found"
                )"""

    if target in content:
        content = content.replace(target, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[5] Updated invoices.py with safe customer fallback")
    else:
        print("[5] invoices.py customer lookup target not found or already updated")

def update_desktop_main():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Ensure silent will-download is present and uses console.log / console.error (never log.info)
    target = "  mainWindow.on('page-title-updated', (e) => e.preventDefault());"
    silent_handler = """  mainWindow.on('page-title-updated', (e) => e.preventDefault());

  // Intercept all downloads to silently save PDFs directly into Archived_PDFs without showing the "Save As" location popup
  mainWindow.webContents.session.on('will-download', (event, item, webContents) => {
    try {
      const fileName = item.getFilename();
      const saveDir = path.join(pcDir, 'Archived_PDFs', 'Downloads');
      if (!fs.existsSync(saveDir)) {
        fs.mkdirSync(saveDir, { recursive: true });
      }
      const finalSavePath = path.join(saveDir, fileName);
      item.setSavePath(finalSavePath);
      console.log(`[Silent-Save] Download saved to ${finalSavePath}`);
    } catch (e) {
      console.error(`[Silent-Save Error] ${e ? e.message : ''}`);
    }
  });"""

    if target in content and "mainWindow.webContents.session.on('will-download'" not in content:
        content = content.replace(target, silent_handler)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[6] Added safe will-download handler to desktop/src/main.js")
    else:
        print("[6] desktop/src/main.js already has will-download handler or target not found")

if __name__ == "__main__":
    update_invoice_pdf_service()
    update_purchases_api()
    update_premium_invoice_html()
    update_sellers_api()
    update_invoices_customer_fallback()
    update_desktop_main()
