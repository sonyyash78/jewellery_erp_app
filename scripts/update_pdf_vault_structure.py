import re
from pathlib import Path

archive_file = r'c:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\pdf_archive_service.py'
with open(archive_file, 'r', encoding='utf-8') as f:
    code = f.read()

# Helper function definition to add near top
helper_func = '''
def get_gst_subfolder(company_id: Optional[int], doc_number: Optional[str]) -> str:
    """Returns 'GST' if company_id == 2 or document number indicates GST, else 'Without_GST'."""
    if company_id == 2:
        return "GST"
    if doc_number:
        clean = str(doc_number).upper()
        if clean.startswith(("SJ/S", "SJ_S", "SJ/P", "SJ_P", "SJ/E", "SJ_E", "PG/S", "PG_S", "PG/P", "PG_P", "PG/E", "PG_E")):
            return "GST"
        if "/S/" in clean or "/P/" in clean or "/E/" in clean:
            return "GST"
    return "Without_GST"
'''

if 'def get_gst_subfolder' not in code:
    code = code.replace('def _sanitize_name(', helper_func + '\ndef _sanitize_name(', 1)
    print("Added get_gst_subfolder helper")

# Replace archive_all_store_documents
old_archive_all_start = "def archive_all_store_documents(db: Session, store_id: int, base_dir: Path, force_refresh: bool = False) -> Dict[str, Any]:"
old_archive_all_end = "def get_all_archive_roots() -> List[Path]:"

archive_all_idx = code.find(old_archive_all_start)
roots_idx = code.find(old_archive_all_end)

assert archive_all_idx != -1 and roots_idx != -1, "Could not find archive_all_store_documents bounds"

new_archive_all = '''def archive_all_store_documents(db: Session, store_id: int, base_dir: Path, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Scans the database and exports all documents into:
    base_dir / "Archived_PDFs" /
        GST /
            Purchases / [Supplier_Name] / ([Purchase_No].pdf + Statement)
            Sales / [Customer_Name] / ([Invoice_No].pdf + Statement)
            Exchanges / [Customer_Name] / ([Exchange_No].pdf)
        Without_GST /
            Purchases / [Supplier_Name] / ([Purchase_No].pdf + Statement)
            Sales / [Customer_Name] / ([Invoice_No].pdf + Statement)
            Exchanges / [Customer_Name] / ([Exchange_No].pdf)
    """
    store_info = _get_store_header(db, store_id)
    archive_root = base_dir / "Archived_PDFs"

    for g_sub in ["GST", "Without_GST"]:
        for cat in ["Sales", "Purchases", "Exchanges"]:
            (archive_root / g_sub / cat).mkdir(parents=True, exist_ok=True)

    counts = {
        "sales_invoices": 0,
        "exchanges": 0,
        "customer_statements": 0,
        "purchases": 0,
        "supplier_statements": 0,
        "total_files": 0
    }

    from app.services.invoice_pdf_service import InvoicePDFService
    from app.services.luxury_pdf_service import (
        generate_luxury_bill_html,
        generate_luxury_statement_html,
        render_html_to_pdf
    )
    from app.services.gst_pdf_template import generate_gst_tax_invoice_html

    sellers = db.query(Seller).filter(Seller.store_id == store_id).all()
    seller_map = {s.id: s for s in sellers}

    customers = db.query(Customer).filter(Customer.store_id == store_id).all()
    cust_map = {c.id: c for c in customers}

    # 1. PROCESS PURCHASES
    from app.models.purchase import PurchaseStatus
    all_purchases = db.query(Purchase).filter(
        Purchase.store_id == store_id,
        Purchase.status != PurchaseStatus.CANCELLED,
        Purchase.status != "CANCELLED"
    ).all()

    for pur in all_purchases:
        s_obj = seller_map.get(pur.seller_id) if pur.seller_id else None
        folder_name = _sanitize_name(s_obj.name, default=f"Supplier_{pur.seller_id}") if s_obj else "Suppliers"
        is_gst = (pur.company_id == 2) or bool(str(getattr(pur, 'purchase_number', '')).startswith(('SJ/P', 'PG/P', 'SJ_', 'PG_'))) or ('/P/' in str(getattr(pur, 'purchase_number', '')))
        gst_folder = "GST" if is_gst else "Without_GST"
        
        target_dir = archive_root / gst_folder / "Purchases" / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        p_no = _sanitize_name(getattr(pur, 'purchase_number', None) or f"PUR-{pur.id}")
        pur_pdf = target_dir / f"{p_no}.pdf"

        if force_refresh or not pur_pdf.exists():
            try:
                p_data = InvoicePDFService.get_purchase_pdf_data(pur.id, db)
                p_html = generate_luxury_bill_html(p_data)
                if not render_html_to_pdf(p_html, pur_pdf):
                    generate_purchase_pdf(pur, store_info, pur_pdf)
                counts["purchases"] += 1
                counts["total_files"] += 1
            except Exception as e:
                try:
                    generate_purchase_pdf(pur, store_info, pur_pdf)
                    counts["purchases"] += 1
                    counts["total_files"] += 1
                except Exception as e2:
                    print(f"[Archive] Error generating purchase PDF {p_no}: {e2}")
        else:
            counts["purchases"] += 1

        rel_path = Path(gst_folder) / "Purchases" / folder_name / f"{p_no}.pdf"
        _save_pdf_to_roots(pur_pdf, rel_path)

    # 2. PROCESS SUPPLIER STATEMENTS
    for s in sellers:
        folder_name = _sanitize_name(s.name, default=f"Supplier_{s.id}")
        entries = []
        try:
            ledgers = db.query(SupplierLedger).filter(SupplierLedger.seller_id == s.id).order_by(SupplierLedger.date.asc()).all()
            for l in ledgers:
                entries.append({
                    "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                    "type": l.voucher_type or "Ledger",
                    "number": l.voucher_number or "-",
                    "description": l.description or "-",
                    "debit": float(l.debit or 0.0),
                    "credit": float(l.credit or 0.0),
                    "balance": float(l.balance or 0.0),
                    "gold_debit": float(getattr(l, "gold_debit", 0.0) or 0.0),
                    "gold_credit": float(getattr(l, "gold_credit", 0.0) or 0.0),
                })
            s_html = generate_luxury_statement_html(
                s.name, s.mobile or "", "Supplier", entries, store_info,
                float(s.current_balance or 0.0), float(getattr(s, "fine_gold_balance", 0.0) or 0.0), float(getattr(s, "fine_silver_balance", 0.0) or 0.0)
            )
            for g_sub in ["GST", "Without_GST"]:
                s_dir = archive_root / g_sub / "Purchases" / folder_name
                if s_dir.exists():
                    stmt_pdf = s_dir / f"Statement_{_sanitize_name(s.name)}.pdf"
                    if force_refresh or not stmt_pdf.exists():
                        if not render_html_to_pdf(s_html, stmt_pdf):
                            generate_supplier_statement_pdf(s, db, store_info, stmt_pdf)
                        counts["supplier_statements"] += 1
                        counts["total_files"] += 1
                    rel_path = Path(g_sub) / "Purchases" / folder_name / f"Statement_{_sanitize_name(s.name)}.pdf"
                    _save_pdf_to_roots(stmt_pdf, rel_path)
        except Exception as e:
            print(f"[Archive] Error generating supplier statement for {s.name}: {e}")

    # 3. PROCESS SALES INVOICES
    from app.models.invoice import InvoiceStatus
    all_invoices = db.query(Invoice).filter(
        Invoice.store_id == store_id,
        Invoice.status != InvoiceStatus.CANCELLED,
        Invoice.status != "Cancelled"
    ).all()

    for inv in all_invoices:
        c_obj = cust_map.get(inv.customer_id) if inv.customer_id else None
        if c_obj:
            c_full = f"{c_obj.first_name} {c_obj.last_name or ''}".strip()
            folder_name = _sanitize_name(c_full, default=f"Customer_{inv.customer_id}")
        else:
            b_name = getattr(inv, 'buyer_name', None) or "Walkin_Customer"
            folder_name = _sanitize_name(b_name, default="Walkin_Customers")

        is_gst = (inv.company_id == 2) or bool(str(getattr(inv, 'invoice_number', '')).startswith(('SJ/S', 'PG/S', 'SJ_', 'PG_'))) or ('/S/' in str(getattr(inv, 'invoice_number', '')))
        gst_folder = "GST" if is_gst else "Without_GST"

        target_dir = archive_root / gst_folder / "Sales" / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        inv_no = _sanitize_name(inv.invoice_number or f"INV-{inv.id}")
        inv_pdf = target_dir / f"{inv_no}.pdf"

        if force_refresh or not inv_pdf.exists():
            try:
                inv_data = InvoicePDFService.get_invoice_pdf_data(inv.id, db)
                if is_gst:
                    inv_html = generate_gst_tax_invoice_html(inv_data)
                else:
                    inv_html = generate_luxury_bill_html(inv_data)

                if not render_html_to_pdf(inv_html, inv_pdf):
                    generate_invoice_pdf(inv, store_info, inv_pdf)

                counts["sales_invoices"] += 1
                counts["total_files"] += 1
            except Exception as e:
                try:
                    generate_invoice_pdf(inv, store_info, inv_pdf)
                    counts["sales_invoices"] += 1
                    counts["total_files"] += 1
                except Exception as e2:
                    print(f"[Archive] Error generating invoice PDF {inv_no}: {e2}")
        else:
            counts["sales_invoices"] += 1

        rel_path = Path(gst_folder) / "Sales" / folder_name / f"{inv_no}.pdf"
        _save_pdf_to_roots(inv_pdf, rel_path)

    # 4. PROCESS EXCHANGES
    all_exchanges = db.query(Exchange).filter(
        Exchange.store_id == store_id,
        getattr(Exchange, 'status', None) != "Cancelled"
    ).all()

    for exc in all_exchanges:
        c_obj = cust_map.get(exc.customer_id) if exc.customer_id else None
        if c_obj:
            c_full = f"{c_obj.first_name} {c_obj.last_name or ''}".strip()
            folder_name = _sanitize_name(c_full, default=f"Customer_{exc.customer_id}")
        else:
            folder_name = "Walkin_Customers"

        is_gst = (exc.company_id == 2) or bool(str(getattr(exc, 'exchange_number', '')).startswith(('SJ/E', 'PG/E', 'SJ_', 'PG_'))) or ('/E/' in str(getattr(exc, 'exchange_number', '')))
        gst_folder = "GST" if is_gst else "Without_GST"

        target_dir = archive_root / gst_folder / "Exchanges" / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        exc_no = _sanitize_name(getattr(exc, 'exchange_number', None) or f"EXC-{exc.id}")
        exc_pdf = target_dir / f"{exc_no}.pdf"

        if force_refresh or not exc_pdf.exists():
            try:
                exc_data = InvoicePDFService.get_exchange_pdf_data(exc.id, db)
                exc_html = generate_luxury_bill_html(exc_data)
                if not render_html_to_pdf(exc_html, exc_pdf):
                    generate_exchange_pdf(exc, store_info, exc_pdf)
                counts["exchanges"] += 1
                counts["total_files"] += 1
            except Exception as e:
                try:
                    generate_exchange_pdf(exc, store_info, exc_pdf)
                    counts["exchanges"] += 1
                    counts["total_files"] += 1
                except Exception as e2:
                    print(f"[Archive] Error generating exchange PDF {exc_no}: {e2}")
        else:
            counts["exchanges"] += 1

        rel_path = Path(gst_folder) / "Exchanges" / folder_name / f"{exc_no}.pdf"
        _save_pdf_to_roots(exc_pdf, rel_path)

    # 5. PROCESS CUSTOMER STATEMENTS
    for c in customers:
        c_full = f"{c.first_name} {c.last_name or ''}".strip()
        folder_name = _sanitize_name(c_full, default=f"Customer_{c.id}")
        entries = []
        try:
            ledgers = db.query(CustomerLedger).filter(CustomerLedger.customer_id == c.id).order_by(CustomerLedger.date.asc()).all()
            for l in ledgers:
                entries.append({
                    "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                    "type": l.voucher_type or "Ledger",
                    "number": l.voucher_number or "-",
                    "description": l.description or "-",
                    "debit": float(l.debit or 0.0),
                    "credit": float(l.credit or 0.0),
                    "balance": float(l.balance or 0.0),
                    "gold_debit": float(l.gold_debit or 0.0),
                    "gold_credit": float(l.gold_credit or 0.0),
                })
            c_html = generate_luxury_statement_html(
                c_full, c.phone_number or "", "Customer", entries, store_info,
                float(c.outstanding_balance or 0.0), float(c.fine_gold_balance or 0.0), float(c.fine_silver_balance or 0.0)
            )
            for g_sub in ["GST", "Without_GST"]:
                c_dir = archive_root / g_sub / "Sales" / folder_name
                if c_dir.exists():
                    stmt_pdf = c_dir / f"Statement_{_sanitize_name(c_full)}.pdf"
                    if force_refresh or not stmt_pdf.exists():
                        if not render_html_to_pdf(c_html, stmt_pdf):
                            generate_customer_statement_pdf(c, db, store_info, stmt_pdf)
                        counts["customer_statements"] += 1
                        counts["total_files"] += 1
                    rel_path = Path(g_sub) / "Sales" / folder_name / f"Statement_{_sanitize_name(c_full)}.pdf"
                    _save_pdf_to_roots(stmt_pdf, rel_path)
        except Exception as e:
            print(f"[Archive] Error generating customer statement for {c_full}: {e}")

    return {
        "status": "success",
        "counts": counts,
        "archive_dir": str(archive_root)
    }

'''

code = code[:archive_all_idx] + new_archive_all + code[roots_idx:]
print("Replaced archive_all_store_documents")

# Now update archive_single_invoice, archive_single_exchange, archive_single_purchase, statements
single_inv_pattern = r'def archive_single_invoice\(invoice_id: int, db: Session = None\):[\s\S]*?def archive_single_exchange'

new_single_inv = '''def archive_single_invoice(invoice_id: int, db: Session = None):
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        from app.services.invoice_pdf_service import InvoicePDFService
        from app.services.luxury_pdf_service import generate_luxury_bill_html, render_html_to_pdf
        from app.core.config import DATA_DIR
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            return
        store_info = _get_store_header(db, inv.store_id or 1)
        c_obj = db.query(Customer).filter(Customer.id == inv.customer_id).first() if inv.customer_id else None
        if c_obj:
            c_full = f"{c_obj.first_name} {c_obj.last_name or ''}".strip()
            folder_name = _sanitize_name(c_full, default=f"Customer_{inv.customer_id}")
        else:
            b_name = getattr(inv, 'buyer_name', None) or "Walkin_Customer"
            folder_name = _sanitize_name(b_name, default="Walkin_Customers")

        is_gst = (inv.company_id == 2) or bool(str(getattr(inv, 'invoice_number', '')).startswith(('SJ/S', 'PG/S', 'SJ_', 'PG_'))) or ('/S/' in str(getattr(inv, 'invoice_number', '')))
        gst_folder = "GST" if is_gst else "Without_GST"

        inv_no = _sanitize_name(inv.invoice_number or f"INV-{inv.id}")
        file_name = f"{inv_no}.pdf"
        rel_path = Path(gst_folder) / "Sales" / folder_name / file_name

        primary_pdf = DATA_DIR / "Archived_PDFs" / rel_path
        primary_pdf.parent.mkdir(parents=True, exist_ok=True)

        inv_data = InvoicePDFService.get_invoice_pdf_data(inv.id, db)
        if is_gst:
            from app.services.gst_pdf_template import generate_gst_tax_invoice_html
            inv_html = generate_gst_tax_invoice_html(inv_data)
        else:
            inv_html = generate_luxury_bill_html(inv_data)

        if not render_html_to_pdf(inv_html, primary_pdf):
            generate_invoice_pdf(inv, store_info, primary_pdf)

        _save_pdf_to_roots(primary_pdf, rel_path)

        if inv.customer_id:
            archive_single_customer_statement(inv.customer_id, db)
    except Exception as e:
        print(f"[Archive Single Invoice Error] {e}")
    finally:
        if close_db:
            db.close()

def archive_single_exchange'''

code = re.sub(single_inv_pattern, new_single_inv, code, count=1)
print("Updated archive_single_invoice")

# Update archive_single_exchange
single_exc_pattern = r'def archive_single_exchange\(exchange_id: int, db: Session = None\):[\s\S]*?def archive_single_purchase'

new_single_exc = '''def archive_single_exchange(exchange_id: int, db: Session = None):
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        from app.services.invoice_pdf_service import InvoicePDFService
        from app.services.luxury_pdf_service import generate_luxury_bill_html, render_html_to_pdf
        from app.core.config import DATA_DIR
        exc = db.query(Exchange).filter(Exchange.id == exchange_id).first()
        if not exc:
            return
        store_info = _get_store_header(db, exc.store_id or 1)
        c_obj = db.query(Customer).filter(Customer.id == exc.customer_id).first() if exc.customer_id else None
        if c_obj:
            c_full = f"{c_obj.first_name} {c_obj.last_name or ''}".strip()
            folder_name = _sanitize_name(c_full, default=f"Customer_{exc.customer_id}")
        else:
            folder_name = "Walkin_Customers"

        is_gst = (exc.company_id == 2) or bool(str(getattr(exc, 'exchange_number', '')).startswith(('SJ/E', 'PG/E', 'SJ_', 'PG_'))) or ('/E/' in str(getattr(exc, 'exchange_number', '')))
        gst_folder = "GST" if is_gst else "Without_GST"

        exc_no = _sanitize_name(getattr(exc, 'exchange_number', None) or f"EXC-{exc.id}")
        file_name = f"{exc_no}.pdf"
        rel_path = Path(gst_folder) / "Exchanges" / folder_name / file_name

        primary_pdf = DATA_DIR / "Archived_PDFs" / rel_path
        primary_pdf.parent.mkdir(parents=True, exist_ok=True)

        exc_data = InvoicePDFService.get_exchange_pdf_data(exc.id, db)
        exc_html = generate_luxury_bill_html(exc_data)
        if not render_html_to_pdf(exc_html, primary_pdf):
            generate_exchange_pdf(exc, store_info, primary_pdf)

        _save_pdf_to_roots(primary_pdf, rel_path)

        if exc.customer_id:
            archive_single_customer_statement(exc.customer_id, db)
    except Exception as e:
        print(f"[Archive Single Exchange Error] {e}")
    finally:
        if close_db:
            db.close()

def archive_single_purchase'''

code = re.sub(single_exc_pattern, new_single_exc, code, count=1)
print("Updated archive_single_exchange")

# Update archive_single_purchase
single_pur_pattern = r'def archive_single_purchase\(purchase_id: int, db: Session = None\):[\s\S]*?def archive_single_customer_statement'

new_single_pur = '''def archive_single_purchase(purchase_id: int, db: Session = None):
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        from app.services.invoice_pdf_service import InvoicePDFService
        from app.services.luxury_pdf_service import generate_luxury_bill_html, render_html_to_pdf
        from app.core.config import DATA_DIR
        pur = db.query(Purchase).filter(Purchase.id == purchase_id).first()
        if not pur:
            return
        store_info = _get_store_header(db, pur.store_id or 1)
        s_obj = db.query(Seller).filter(Seller.id == pur.seller_id).first() if pur.seller_id else None
        if s_obj:
            folder_name = _sanitize_name(s_obj.name, default=f"Supplier_{pur.seller_id}")
        else:
            folder_name = "Suppliers"

        is_gst = (pur.company_id == 2) or bool(str(getattr(pur, 'purchase_number', '')).startswith(('SJ/P', 'PG/P', 'SJ_', 'PG_'))) or ('/P/' in str(getattr(pur, 'purchase_number', '')))
        gst_folder = "GST" if is_gst else "Without_GST"

        p_no = _sanitize_name(getattr(pur, 'purchase_number', None) or f"PUR-{pur.id}")
        file_name = f"{p_no}.pdf"
        rel_path = Path(gst_folder) / "Purchases" / folder_name / file_name

        primary_pdf = DATA_DIR / "Archived_PDFs" / rel_path
        primary_pdf.parent.mkdir(parents=True, exist_ok=True)

        pur_data = InvoicePDFService.get_purchase_pdf_data(pur.id, db)
        pur_html = generate_luxury_bill_html(pur_data)
        if not render_html_to_pdf(pur_html, primary_pdf):
            generate_purchase_pdf(pur, store_info, primary_pdf)

        _save_pdf_to_roots(primary_pdf, rel_path)

        if pur.seller_id:
            archive_single_supplier_statement(pur.seller_id, db)
    except Exception as e:
        print(f"[Archive Single Purchase Error] {e}")
    finally:
        if close_db:
            db.close()

def archive_single_customer_statement'''

code = re.sub(single_pur_pattern, new_single_pur, code, count=1)
print("Updated archive_single_purchase")

# Update archive_single_customer_statement
single_cust_pattern = r'def archive_single_customer_statement\(customer_id: int, db: Session = None\):[\s\S]*?def archive_single_supplier_statement'

new_single_cust = '''def archive_single_customer_statement(customer_id: int, db: Session = None):
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        from app.services.luxury_pdf_service import generate_luxury_statement_html, render_html_to_pdf
        from app.core.config import DATA_DIR
        c = db.query(Customer).filter(Customer.id == customer_id).first()
        if not c:
            return
        store_info = _get_store_header(db, c.store_id or 1)
        c_full = f"{c.first_name} {c.last_name or ''}".strip()
        folder_name = _sanitize_name(c_full, default=f"Customer_{c.id}")

        entries = []
        ledgers = db.query(CustomerLedger).filter(CustomerLedger.customer_id == c.id).order_by(CustomerLedger.date.asc()).all()
        for l in ledgers:
            entries.append({
                "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                "type": l.voucher_type or "Ledger",
                "number": l.voucher_number or "-",
                "description": l.description or "-",
                "debit": float(l.debit or 0.0),
                "credit": float(l.credit or 0.0),
                "balance": float(l.balance or 0.0),
                "gold_debit": float(l.gold_debit or 0.0),
                "gold_credit": float(l.gold_credit or 0.0),
            })

        c_html = generate_luxury_statement_html(
            c_full, c.phone_number or "", "Customer", entries, store_info,
            float(c.outstanding_balance or 0.0), float(c.fine_gold_balance or 0.0), float(c.fine_silver_balance or 0.0)
        )

        for g_sub in ["GST", "Without_GST"]:
            rel_path = Path(g_sub) / "Sales" / folder_name / f"Statement_{_sanitize_name(c_full)}.pdf"
            primary_pdf = DATA_DIR / "Archived_PDFs" / rel_path
            primary_pdf.parent.mkdir(parents=True, exist_ok=True)
            if not render_html_to_pdf(c_html, primary_pdf):
                generate_customer_statement_pdf(c, db, store_info, primary_pdf)
            _save_pdf_to_roots(primary_pdf, rel_path)

    except Exception as e:
        print(f"[Archive Customer Statement Error] {e}")
    finally:
        if close_db:
            db.close()

def archive_single_supplier_statement'''

code = re.sub(single_cust_pattern, new_single_cust, code, count=1)
print("Updated archive_single_customer_statement")

# Update archive_single_supplier_statement
single_supp_pattern = r'def archive_single_supplier_statement\(seller_id: int, db: Session = None\):[\s\S]*?def dispatch_async_archive'

new_single_supp = '''def archive_single_supplier_statement(seller_id: int, db: Session = None):
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        from app.services.luxury_pdf_service import generate_luxury_statement_html, render_html_to_pdf
        from app.core.config import DATA_DIR
        s = db.query(Seller).filter(Seller.id == seller_id).first()
        if not s:
            return
        store_info = _get_store_header(db, s.store_id or 1)
        folder_name = _sanitize_name(s.name, default=f"Supplier_{s.id}")

        entries = []
        ledgers = db.query(SupplierLedger).filter(SupplierLedger.seller_id == s.id).order_by(SupplierLedger.date.asc()).all()
        for l in ledgers:
            entries.append({
                "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                "type": l.voucher_type or "Ledger",
                "number": l.voucher_number or "-",
                "description": l.description or "-",
                "debit": float(l.debit or 0.0),
                "credit": float(l.credit or 0.0),
                "balance": float(l.balance or 0.0),
                "gold_debit": float(getattr(l, "gold_debit", 0.0) or 0.0),
                "gold_credit": float(getattr(l, "gold_credit", 0.0) or 0.0),
            })

        s_html = generate_luxury_statement_html(
            s.name, s.mobile or "", "Supplier", entries, store_info,
            float(s.current_balance or 0.0), float(getattr(s, "fine_gold_balance", 0.0) or 0.0), float(getattr(s, "fine_silver_balance", 0.0) or 0.0)
        )

        for g_sub in ["GST", "Without_GST"]:
            rel_path = Path(g_sub) / "Purchases" / folder_name / f"Statement_{_sanitize_name(s.name)}.pdf"
            primary_pdf = DATA_DIR / "Archived_PDFs" / rel_path
            primary_pdf.parent.mkdir(parents=True, exist_ok=True)
            if not render_html_to_pdf(s_html, primary_pdf):
                generate_supplier_statement_pdf(s, db, store_info, primary_pdf)
            _save_pdf_to_roots(primary_pdf, rel_path)

    except Exception as e:
        print(f"[Archive Supplier Statement Error] {e}")
    finally:
        if close_db:
            db.close()

def dispatch_async_archive'''

code = re.sub(single_supp_pattern, new_single_supp, code, count=1)
print("Updated archive_single_supplier_statement")

with open(archive_file, 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved pdf_archive_service.py successfully!")
