import re

report_service_path = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\report_service.py'

with open(report_service_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure DiamondCalculation is imported
if 'from app.models.diamond_calculation import DiamondCalculation' not in content:
    content = content.replace(
        'from app.models.silver_rate import SilverRate',
        'from app.models.silver_rate import SilverRate\nfrom app.models.diamond_calculation import DiamondCalculation'
    )

new_wastage_method = '''    @staticmethod
    def get_company_wastage_analysis(
        db: Session,
        company_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Metal Wastage & Margin Profit Report:
        Calculates separate wastage (Ghat) and making/labour profit for Gold, Silver, and Diamond:
        Net Wastage Profit (g) = Customer Sold Wastage (g) - Supplier Purchased Wastage (g)
        """
        start_dt, end_dt = _dt_range(start_date, end_date)

        # -------------------------------------------------------------
        # 1. GOLD ANALYSIS
        # -------------------------------------------------------------
        # 1a. Sold Gold (Invoices)
        g_sold_q = db.query(
            func.coalesce(func.sum(GoldCalculation.net_weight * GoldCalculation.wastage / 100), 0),
            func.coalesce(func.sum(GoldCalculation.fine_weight), 0),
            func.coalesce(func.sum(GoldCalculation.making_charges_amount), 0),
            func.coalesce(func.sum(GoldCalculation.total_gold_value), 0)
        ).join(InvoiceItem, InvoiceItem.id == GoldCalculation.invoice_item_id)\\
         .join(Invoice, Invoice.id == InvoiceItem.invoice_id)\\
         .filter(Invoice.company_id == company_id, Invoice.status != InvoiceStatus.CANCELLED)

        if start_dt:
            g_sold_q = g_sold_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            g_sold_q = g_sold_q.filter(Invoice.invoice_date <= end_dt)

        g_sold_w, g_sold_fine, g_sold_making, g_sold_val = g_sold_q.first()

        # 1b. Purchased Gold (Purchases)
        g_pur_q = db.query(
            func.coalesce(func.sum(PurchaseItem.net_weight * PurchaseItem.wastage / 100), 0),
            func.coalesce(func.sum(PurchaseItem.fine_weight), 0),
            func.coalesce(func.sum(PurchaseItem.labour_charge), 0),
            func.coalesce(func.sum(PurchaseItem.taxable_amount), 0)
        ).join(Purchase, Purchase.id == PurchaseItem.purchase_id)\\
         .filter(Purchase.company_id == company_id, Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'gold')

        if start_dt:
            g_pur_q = g_pur_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            g_pur_q = g_pur_q.filter(Purchase.created_at <= end_dt)

        g_pur_w, g_pur_fine, g_pur_labour, g_pur_val = g_pur_q.first()

        gold_sold_wastage = Decimal(str(g_sold_w or 0))
        gold_pur_wastage = Decimal(str(g_pur_w or 0))
        gold_net_wastage_profit = gold_sold_wastage - gold_pur_wastage

        gold_sold_making = Decimal(str(g_sold_making or 0))
        gold_pur_labour = Decimal(str(g_pur_labour or 0))
        gold_net_labour_profit = gold_sold_making - gold_pur_labour

        gold_sold_val = Decimal(str(g_sold_val or 0))
        gold_pur_val = Decimal(str(g_pur_val or 0))
        gold_net_val_profit = gold_sold_val - gold_pur_val

        # -------------------------------------------------------------
        # 2. SILVER ANALYSIS
        # -------------------------------------------------------------
        # 2a. Sold Silver (Invoices)
        s_sold_q = db.query(
            func.coalesce(func.sum(SilverCalculation.wastage * (SilverCalculation.gross_weight - SilverCalculation.stone_weight) / 100), 0),
            func.coalesce(func.sum(SilverCalculation.pure_weight), 0),
            func.coalesce(func.sum(SilverCalculation.making_charges_amount), 0),
            func.coalesce(func.sum(SilverCalculation.total_silver_value), 0)
        ).join(InvoiceItem, InvoiceItem.id == SilverCalculation.invoice_item_id)\\
         .join(Invoice, Invoice.id == InvoiceItem.invoice_id)\\
         .filter(Invoice.company_id == company_id, Invoice.status != InvoiceStatus.CANCELLED)

        if start_dt:
            s_sold_q = s_sold_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            s_sold_q = s_sold_q.filter(Invoice.invoice_date <= end_dt)

        s_sold_w, s_sold_pure, s_sold_making, s_sold_val = s_sold_q.first()

        # 2b. Purchased Silver (Purchases)
        s_pur_q = db.query(
            func.coalesce(func.sum(PurchaseItem.net_weight * PurchaseItem.wastage / 100), 0),
            func.coalesce(func.sum(PurchaseItem.fine_weight), 0),
            func.coalesce(func.sum(PurchaseItem.labour_charge), 0),
            func.coalesce(func.sum(PurchaseItem.taxable_amount), 0)
        ).join(Purchase, Purchase.id == PurchaseItem.purchase_id)\\
         .filter(Purchase.company_id == company_id, Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'silver')

        if start_dt:
            s_pur_q = s_pur_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            s_pur_q = s_pur_q.filter(Purchase.created_at <= end_dt)

        s_pur_w, s_pur_pure, s_pur_labour, s_pur_val = s_pur_q.first()

        silver_sold_wastage = Decimal(str(s_sold_w or 0))
        silver_pur_wastage = Decimal(str(s_pur_w or 0))
        silver_net_wastage_profit = silver_sold_wastage - silver_pur_wastage

        silver_sold_making = Decimal(str(s_sold_making or 0))
        silver_pur_labour = Decimal(str(s_pur_labour or 0))
        silver_net_labour_profit = silver_sold_making - silver_pur_labour

        silver_sold_val = Decimal(str(s_sold_val or 0))
        silver_pur_val = Decimal(str(s_pur_val or 0))
        silver_net_val_profit = silver_sold_val - silver_pur_val

        # -------------------------------------------------------------
        # 3. DIAMOND ANALYSIS
        # -------------------------------------------------------------
        # 3a. Sold Diamond (Invoices)
        d_sold_q = db.query(
            func.coalesce(func.sum(DiamondCalculation.carat_weight), 0),
            func.coalesce(func.sum(DiamondCalculation.weight_gm), 0),
            func.coalesce(func.sum(DiamondCalculation.making_charges), 0),
            func.coalesce(func.sum(DiamondCalculation.total_diamond_value), 0)
        ).join(InvoiceItem, InvoiceItem.id == DiamondCalculation.invoice_item_id)\\
         .join(Invoice, Invoice.id == InvoiceItem.invoice_id)\\
         .filter(Invoice.company_id == company_id, Invoice.status != InvoiceStatus.CANCELLED)

        if start_dt:
            d_sold_q = d_sold_q.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            d_sold_q = d_sold_q.filter(Invoice.invoice_date <= end_dt)

        d_sold_cts, d_sold_gm, d_sold_making, d_sold_val = d_sold_q.first()

        # 3b. Purchased Diamond (Purchases)
        d_pur_q = db.query(
            func.coalesce(func.sum(PurchaseItem.gross_weight), 0),
            func.coalesce(func.sum(PurchaseItem.labour_charge), 0),
            func.coalesce(func.sum(PurchaseItem.taxable_amount), 0)
        ).join(Purchase, Purchase.id == PurchaseItem.purchase_id)\\
         .filter(Purchase.company_id == company_id, Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'diamond')

        if start_dt:
            d_pur_q = d_pur_q.filter(Purchase.created_at >= start_dt)
        if end_dt:
            d_pur_q = d_pur_q.filter(Purchase.created_at <= end_dt)

        d_pur_wt, d_pur_labour, d_pur_val = d_pur_q.first()

        diamond_sold_cts = Decimal(str(d_sold_cts or 0))
        diamond_sold_making = Decimal(str(d_sold_making or 0))
        diamond_pur_labour = Decimal(str(d_pur_labour or 0))
        diamond_net_making_profit = diamond_sold_making - diamond_pur_labour

        diamond_sold_val = Decimal(str(d_sold_val or 0))
        diamond_pur_val = Decimal(str(d_pur_val or 0))
        diamond_net_val_profit = diamond_sold_val - diamond_pur_val

        # -------------------------------------------------------------
        # 4. RECENT TRANSACTION LINE ITEMS
        # -------------------------------------------------------------
        transactions = []

        # Gold sales lines
        g_lines = db.query(
            Invoice.invoice_date,
            Invoice.invoice_number,
            InvoiceItem.item_name,
            GoldCalculation.gross_weight,
            GoldCalculation.touch_purity,
            GoldCalculation.wastage,
            GoldCalculation.fine_weight,
            GoldCalculation.making_charges_amount,
            GoldCalculation.total_gold_value
        ).join(InvoiceItem, InvoiceItem.id == GoldCalculation.invoice_item_id)\\
         .join(Invoice, Invoice.id == InvoiceItem.invoice_id)\\
         .filter(Invoice.company_id == company_id, Invoice.status != InvoiceStatus.CANCELLED)
        if start_dt:
            g_lines = g_lines.filter(Invoice.invoice_date >= start_dt)
        if end_dt:
            g_lines = g_lines.filter(Invoice.invoice_date <= end_dt)

        for row in g_lines.order_by(Invoice.invoice_date.desc()).limit(20).all():
            w_gms = float(Decimal(str(row[3] or 0)) * Decimal(str(row[5] or 0)) / Decimal('100'))
            transactions.append({
                "date": row[0].strftime("%Y-%m-%d") if row[0] else "",
                "type": "Sale",
                "bill_no": row[1],
                "item_name": row[2] or "Gold Item",
                "metal": "Gold",
                "weight_g": float(row[3] or 0),
                "touch_pct": float(row[4] or 0),
                "wastage_pct": float(row[5] or 0),
                "wastage_g": round(w_gms, 3),
                "fine_weight_g": float(row[6] or 0),
                "making_charges": float(row[7] or 0),
                "total_amount": float(row[8] or 0)
            })

        # Gold purchase lines
        g_pur_lines = db.query(
            Purchase.created_at,
            Purchase.purchase_number,
            PurchaseItem.item_name,
            PurchaseItem.gross_weight,
            PurchaseItem.touch_purity,
            PurchaseItem.wastage,
            PurchaseItem.fine_weight,
            PurchaseItem.labour_charge,
            PurchaseItem.taxable_amount
        ).join(Purchase, Purchase.id == PurchaseItem.purchase_id)\\
         .filter(Purchase.company_id == company_id, Purchase.status != PurchaseStatus.CANCELLED, func.lower(PurchaseItem.metal_type) == 'gold')
        if start_dt:
            g_pur_lines = g_pur_lines.filter(Purchase.created_at >= start_dt)
        if end_dt:
            g_pur_lines = g_pur_lines.filter(Purchase.created_at <= end_dt)

        for row in g_pur_lines.order_by(Purchase.created_at.desc()).limit(20).all():
            w_gms = float(Decimal(str(row[3] or 0)) * Decimal(str(row[5] or 0)) / Decimal('100'))
            transactions.append({
                "date": row[0].strftime("%Y-%m-%d") if row[0] else "",
                "type": "Purchase",
                "bill_no": row[1],
                "item_name": row[2] or "Gold Purchase",
                "metal": "Gold",
                "weight_g": float(row[3] or 0),
                "touch_pct": float(row[4] or 0),
                "wastage_pct": float(row[5] or 0),
                "wastage_g": round(w_gms, 3),
                "fine_weight_g": float(row[6] or 0),
                "making_charges": float(row[7] or 0),
                "total_amount": float(row[8] or 0)
            })

        # Total combined profits
        total_making_profit = gold_net_labour_profit + silver_net_labour_profit + diamond_net_making_profit
        total_val_profit = gold_net_val_profit + silver_net_val_profit + diamond_net_val_profit

        return {
            "company_id": company_id,
            "summary": {
                "gold_net_wastage_profit_g": float(round(gold_net_wastage_profit, 3)),
                "silver_net_wastage_profit_g": float(round(silver_net_wastage_profit, 3)),
                "diamond_carats_sold": float(round(diamond_sold_cts, 4)),
                "total_making_profit_rs": float(round(total_making_profit, 2)),
                "total_value_profit_rs": float(round(total_val_profit, 2))
            },
            "gold": {
                "sold_fine_g": float(round(Decimal(str(g_sold_fine or 0)), 3)),
                "sold_wastage_g": float(round(gold_sold_wastage, 3)),
                "sold_making_rs": float(round(gold_sold_making, 2)),
                "sold_total_val_rs": float(round(gold_sold_val, 2)),
                "purchased_fine_g": float(round(Decimal(str(g_pur_fine or 0)), 3)),
                "purchased_wastage_g": float(round(gold_pur_wastage, 3)),
                "purchased_labour_rs": float(round(gold_pur_labour, 2)),
                "purchased_total_val_rs": float(round(gold_pur_val, 2)),
                "net_wastage_profit_g": float(round(gold_net_wastage_profit, 3)),
                "net_labour_profit_rs": float(round(gold_net_labour_profit, 2)),
                "net_val_profit_rs": float(round(gold_net_val_profit, 2))
            },
            "silver": {
                "sold_pure_g": float(round(Decimal(str(s_sold_pure or 0)), 3)),
                "sold_wastage_g": float(round(silver_sold_wastage, 3)),
                "sold_making_rs": float(round(silver_sold_making, 2)),
                "sold_total_val_rs": float(round(silver_sold_val, 2)),
                "purchased_pure_g": float(round(Decimal(str(s_pur_pure or 0)), 3)),
                "purchased_wastage_g": float(round(silver_pur_wastage, 3)),
                "purchased_labour_rs": float(round(silver_pur_labour, 2)),
                "purchased_total_val_rs": float(round(silver_pur_val, 2)),
                "net_wastage_profit_g": float(round(silver_net_wastage_profit, 3)),
                "net_labour_profit_rs": float(round(silver_net_labour_profit, 2)),
                "net_val_profit_rs": float(round(silver_net_val_profit, 2))
            },
            "diamond": {
                "sold_carats": float(round(diamond_sold_cts, 4)),
                "sold_weight_g": float(round(Decimal(str(d_sold_gm or 0)), 3)),
                "sold_making_rs": float(round(diamond_sold_making, 2)),
                "sold_total_val_rs": float(round(diamond_sold_val, 2)),
                "purchased_labour_rs": float(round(diamond_pur_labour, 2)),
                "purchased_total_val_rs": float(round(diamond_pur_val, 2)),
                "net_making_profit_rs": float(round(diamond_net_making_profit, 2)),
                "net_val_profit_rs": float(round(diamond_net_val_profit, 2))
            },
            "transactions": transactions
        }'''

# Replace the old get_company_wastage_analysis in report_service.py
old_pattern = r"    @staticmethod\s+def get_company_wastage_analysis\(.*?\n        \}"
content = re.sub(old_pattern, new_wastage_method, content, flags=re.DOTALL)

with open(report_service_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated report_service.py with comprehensive Wastage & Margin Analysis!")

# Update backend/app/api/v1/reports.py to add /wastage-profit alias route
reports_api_path = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\reports.py'
with open(reports_api_path, 'r', encoding='utf-8') as f:
    api_c = f.read()

if '@router.get("/wastage-profit")' not in api_c:
    alias_route = '''@router.get("/wastage-profit")
def get_wastage_profit_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    company_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Unified Wastage Profit Report for Gold, Silver, and Diamond."""
    resolved_cid = company_id
    if not resolved_cid and x_company_id:
        try:
            resolved_cid = int(x_company_id)
        except ValueError:
            pass
    if not resolved_cid:
        resolved_cid = getattr(current_user, "tenant_id", 1) or 1

    return ReportService.get_company_wastage_analysis(
        db, company_id=resolved_cid, start_date=start_date, end_date=end_date
    )

'''
    api_c = api_c.replace(
        '@router.get("/company-wastage-profit")',
        alias_route + '@router.get("/company-wastage-profit")'
    )

with open(reports_api_path, 'w', encoding='utf-8') as f:
    f.write(api_c)

print("Updated reports.py API with /wastage-profit route!")
