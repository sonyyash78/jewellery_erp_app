import os

file_path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\pdf_archive_service.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update section 2: Supplier statements
old_supplier_sec = """    # 2. PROCESS SUPPLIER STATEMENTS
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
                float(getattr(s, "outstanding_balance", 0.0) or getattr(s, "current_balance", 0.0) or 0.0), float(getattr(s, "fine_gold_balance", 0.0) or 0.0), float(getattr(s, "fine_silver_balance", 0.0) or 0.0)
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
            print(f"[Archive] Error generating supplier statement for {s.name}: {e}")"""

new_supplier_sec = """    # 2. PROCESS SUPPLIER STATEMENTS
    for s in sellers:
        folder_name = _sanitize_name(s.name, default=f"Supplier_{s.id}")
        try:
            all_ledgers = db.query(SupplierLedger).filter(SupplierLedger.seller_id == s.id).order_by(SupplierLedger.date.asc()).all()
            for g_sub in ["GST", "Without_GST"]:
                is_gst_filter = (g_sub == "GST")
                s_dir = archive_root / g_sub / "Purchases" / folder_name
                sub_ledgers = [
                    l for l in all_ledgers
                    if (is_gst_filter and (getattr(l, "company_id", 1) == 2 or "/P/" in str(l.voucher_number or "")))
                    or (not is_gst_filter and getattr(l, "company_id", 1) == 1 and "/P/" not in str(l.voucher_number or ""))
                ]
                if not sub_ledgers:
                    stmt_pdf = s_dir / f"Statement_{_sanitize_name(s.name)}.pdf"
                    if stmt_pdf.exists():
                        try:
                            stmt_pdf.unlink()
                        except Exception:
                            pass
                    continue

                s_dir.mkdir(parents=True, exist_ok=True)
                entries = []
                running_cash = 0.0
                running_gold = 0.0
                running_silver = 0.0
                for l in sub_ledgers:
                    deb = float(l.debit or 0.0)
                    crd = float(l.credit or 0.0)
                    running_cash += (deb - crd)
                    g_deb = float(getattr(l, "gold_debit", 0.0) or 0.0)
                    g_crd = float(getattr(l, "gold_credit", 0.0) or 0.0)
                    running_gold += (g_deb - g_crd)
                    s_deb = float(getattr(l, "silver_debit", 0.0) or 0.0)
                    s_crd = float(getattr(l, "silver_credit", 0.0) or 0.0)
                    running_silver += (s_deb - s_crd)
                    entries.append({
                        "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                        "type": l.voucher_type or "Ledger",
                        "number": l.voucher_number or "-",
                        "description": l.description or "-",
                        "debit": deb,
                        "credit": crd,
                        "balance": running_cash,
                        "gold_debit": g_deb,
                        "gold_credit": g_crd,
                    })

                s_html = generate_luxury_statement_html(
                    s.name, s.mobile or "", "Supplier", entries, store_info,
                    running_cash, running_gold, running_silver
                )
                stmt_pdf = s_dir / f"Statement_{_sanitize_name(s.name)}.pdf"
                if force_refresh or not stmt_pdf.exists():
                    if not render_html_to_pdf(s_html, stmt_pdf):
                        generate_supplier_statement_pdf(s, db, store_info, stmt_pdf)
                    counts["supplier_statements"] += 1
                    counts["total_files"] += 1
                rel_path = Path(g_sub) / "Purchases" / folder_name / f"Statement_{_sanitize_name(s.name)}.pdf"
                _save_pdf_to_roots(stmt_pdf, rel_path)
        except Exception as e:
            print(f"[Archive] Error generating supplier statement for {s.name}: {e}")"""

# 2. Update section 5: Customer statements
old_customer_sec = """    # 5. PROCESS CUSTOMER STATEMENTS
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
            print(f"[Archive] Error generating customer statement for {c_full}: {e}")"""

new_customer_sec = """    # 5. PROCESS CUSTOMER STATEMENTS
    for c in customers:
        c_full = f"{c.first_name} {c.last_name or ''}".strip()
        folder_name = _sanitize_name(c_full, default=f"Customer_{c.id}")
        try:
            all_ledgers = db.query(CustomerLedger).filter(CustomerLedger.customer_id == c.id).order_by(CustomerLedger.date.asc()).all()
            for g_sub in ["GST", "Without_GST"]:
                is_gst_filter = (g_sub == "GST")
                c_dir = archive_root / g_sub / "Sales" / folder_name
                sub_ledgers = [
                    l for l in all_ledgers
                    if (is_gst_filter and (getattr(l, "company_id", 1) == 2 or "/S/" in str(l.voucher_number or "")))
                    or (not is_gst_filter and getattr(l, "company_id", 1) == 1 and "/S/" not in str(l.voucher_number or ""))
                ]
                if not sub_ledgers:
                    stmt_pdf = c_dir / f"Statement_{_sanitize_name(c_full)}.pdf"
                    if stmt_pdf.exists():
                        try:
                            stmt_pdf.unlink()
                        except Exception:
                            pass
                    continue

                c_dir.mkdir(parents=True, exist_ok=True)
                entries = []
                running_cash = 0.0
                running_gold = 0.0
                running_silver = 0.0
                for l in sub_ledgers:
                    deb = float(l.debit or 0.0)
                    crd = float(l.credit or 0.0)
                    running_cash += (deb - crd)
                    g_deb = float(getattr(l, "gold_debit", 0.0) or 0.0)
                    g_crd = float(getattr(l, "gold_credit", 0.0) or 0.0)
                    running_gold += (g_deb - g_crd)
                    s_deb = float(getattr(l, "silver_debit", 0.0) or 0.0)
                    s_crd = float(getattr(l, "silver_credit", 0.0) or 0.0)
                    running_silver += (s_deb - s_crd)
                    entries.append({
                        "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                        "type": l.voucher_type or "Ledger",
                        "number": l.voucher_number or "-",
                        "description": l.description or "-",
                        "debit": deb,
                        "credit": crd,
                        "balance": running_cash,
                        "gold_debit": g_deb,
                        "gold_credit": g_crd,
                    })

                c_html = generate_luxury_statement_html(
                    c_full, c.phone_number or "", "Customer", entries, store_info,
                    running_cash, running_gold, running_silver
                )
                stmt_pdf = c_dir / f"Statement_{_sanitize_name(c_full)}.pdf"
                if force_refresh or not stmt_pdf.exists():
                    if not render_html_to_pdf(c_html, stmt_pdf):
                        generate_customer_statement_pdf(c, db, store_info, stmt_pdf)
                    counts["customer_statements"] += 1
                    counts["total_files"] += 1
                rel_path = Path(g_sub) / "Sales" / folder_name / f"Statement_{_sanitize_name(c_full)}.pdf"
                _save_pdf_to_roots(stmt_pdf, rel_path)
        except Exception as e:
            print(f"[Archive] Error generating customer statement for {c_full}: {e}")"""

# 3. Update single customer & supplier statement functions
old_single_sec = """def archive_single_customer_statement(customer_id: int, db: Session = None):
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

def archive_single_supplier_statement(seller_id: int, db: Session = None):
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
            float(getattr(s, "outstanding_balance", 0.0) or getattr(s, "current_balance", 0.0) or 0.0), float(getattr(s, "fine_gold_balance", 0.0) or 0.0), float(getattr(s, "fine_silver_balance", 0.0) or 0.0)
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
            db.close()"""

new_single_sec = """def archive_single_customer_statement(customer_id: int, db: Session = None):
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

        all_ledgers = db.query(CustomerLedger).filter(CustomerLedger.customer_id == c.id).order_by(CustomerLedger.date.asc()).all()

        for g_sub in ["GST", "Without_GST"]:
            is_gst_filter = (g_sub == "GST")
            sub_ledgers = [
                l for l in all_ledgers
                if (is_gst_filter and (getattr(l, "company_id", 1) == 2 or "/S/" in str(l.voucher_number or "")))
                or (not is_gst_filter and getattr(l, "company_id", 1) == 1 and "/S/" not in str(l.voucher_number or ""))
            ]
            if not sub_ledgers:
                continue

            entries = []
            running_cash = 0.0
            running_gold = 0.0
            running_silver = 0.0
            for l in sub_ledgers:
                deb = float(l.debit or 0.0)
                crd = float(l.credit or 0.0)
                running_cash += (deb - crd)
                g_deb = float(getattr(l, "gold_debit", 0.0) or 0.0)
                g_crd = float(getattr(l, "gold_credit", 0.0) or 0.0)
                running_gold += (g_deb - g_crd)
                s_deb = float(getattr(l, "silver_debit", 0.0) or 0.0)
                s_crd = float(getattr(l, "silver_credit", 0.0) or 0.0)
                running_silver += (s_deb - s_crd)
                entries.append({
                    "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                    "type": l.voucher_type or "Ledger",
                    "number": l.voucher_number or "-",
                    "description": l.description or "-",
                    "debit": deb,
                    "credit": crd,
                    "balance": running_cash,
                    "gold_debit": g_deb,
                    "gold_credit": g_crd,
                })

            c_html = generate_luxury_statement_html(
                c_full, c.phone_number or "", "Customer", entries, store_info,
                running_cash, running_gold, running_silver
            )

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

def archive_single_supplier_statement(seller_id: int, db: Session = None):
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

        all_ledgers = db.query(SupplierLedger).filter(SupplierLedger.seller_id == s.id).order_by(SupplierLedger.date.asc()).all()

        for g_sub in ["GST", "Without_GST"]:
            is_gst_filter = (g_sub == "GST")
            sub_ledgers = [
                l for l in all_ledgers
                if (is_gst_filter and (getattr(l, "company_id", 1) == 2 or "/P/" in str(l.voucher_number or "")))
                or (not is_gst_filter and getattr(l, "company_id", 1) == 1 and "/P/" not in str(l.voucher_number or ""))
            ]
            if not sub_ledgers:
                continue

            entries = []
            running_cash = 0.0
            running_gold = 0.0
            running_silver = 0.0
            for l in sub_ledgers:
                deb = float(l.debit or 0.0)
                crd = float(l.credit or 0.0)
                running_cash += (deb - crd)
                g_deb = float(getattr(l, "gold_debit", 0.0) or 0.0)
                g_crd = float(getattr(l, "gold_credit", 0.0) or 0.0)
                running_gold += (g_deb - g_crd)
                s_deb = float(getattr(l, "silver_debit", 0.0) or 0.0)
                s_crd = float(getattr(l, "silver_credit", 0.0) or 0.0)
                running_silver += (s_deb - s_crd)
                entries.append({
                    "date": (l.date.strftime("%d-%b-%Y") if getattr(l, "date", None) else ""),
                    "type": l.voucher_type or "Ledger",
                    "number": l.voucher_number or "-",
                    "description": l.description or "-",
                    "debit": deb,
                    "credit": crd,
                    "balance": running_cash,
                    "gold_debit": g_deb,
                    "gold_credit": g_crd,
                })

            s_html = generate_luxury_statement_html(
                s.name, s.mobile or "", "Supplier", entries, store_info,
                running_cash, running_gold, running_silver
            )

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
            db.close()"""

# Normalize CRLF
content_norm = content.replace("\r\n", "\n")
old_supplier_sec_norm = old_supplier_sec.replace("\r\n", "\n")
new_supplier_sec_norm = new_supplier_sec.replace("\r\n", "\n")
old_customer_sec_norm = old_customer_sec.replace("\r\n", "\n")
new_customer_sec_norm = new_customer_sec.replace("\r\n", "\n")
old_single_sec_norm = old_single_sec.replace("\r\n", "\n")
new_single_sec_norm = new_single_sec.replace("\r\n", "\n")

if old_supplier_sec_norm in content_norm:
    content_norm = content_norm.replace(old_supplier_sec_norm, new_supplier_sec_norm)
    print("Section 2 (Supplier statements) matched and replaced successfully!")
else:
    print("Warning: old_supplier_sec not found!")

if old_customer_sec_norm in content_norm:
    content_norm = content_norm.replace(old_customer_sec_norm, new_customer_sec_norm)
    print("Section 5 (Customer statements) matched and replaced successfully!")
else:
    print("Warning: old_customer_sec not found!")

if old_single_sec_norm in content_norm:
    content_norm = content_norm.replace(old_single_sec_norm, new_single_sec_norm)
    print("Single statement methods matched and replaced successfully!")
else:
    print("Warning: old_single_sec not found!")

with open(file_path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content_norm)

print("Saved updated pdf_archive_service.py")
