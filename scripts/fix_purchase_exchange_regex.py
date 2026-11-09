import re

def fix_purchases():
    p = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\purchases.py"
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()

    # Fix get_unified_purchases_history
    pattern_hist = r"def get_unified_purchases_history\s*\(\s*skip:\s*int\s*=\s*Query\(0,\s*ge=0\),\s*limit:\s*int\s*=\s*Query\(100,\s*ge=1\),\s*db:\s*Session\s*=\s*Depends\(get_db\),\s*current_user:\s*User\s*=\s*Depends\(get_current_user\)\s*\)\s*->\s*Any:"
    repl_hist = """def get_unified_purchases_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    company_id: Optional[int] = Query(None),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:"""
    c, n_hist = re.subn(pattern_hist, repl_hist, c)
    print("Replaced get_unified_purchases_history:", n_hist)

    # Fix create_unified_purchase
    pattern_create = r"def create_unified_purchase\s*\(\s*purchase_in:\s*UnifiedPurchaseCreate,\s*db:\s*Session\s*=\s*Depends\(get_db\),\s*current_user:\s*User\s*=\s*Depends\(get_current_user\)\s*\)\s*->\s*Any:"
    repl_create = """def create_unified_purchase(
    purchase_in: UnifiedPurchaseCreate,
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:"""
    c, n_create = re.subn(pattern_create, repl_create, c)
    print("Replaced create_unified_purchase:", n_create)

    with open(p, "w", encoding="utf-8") as f:
        f.write(c)

def fix_exchanges():
    p = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\exchanges.py"
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()

    # Fix list_exchanges
    pattern_list = r"def list_exchanges\s*\(\s*skip:\s*int\s*=\s*Query\(0,\s*ge=0\),\s*limit:\s*int\s*=\s*Query\(100,\s*ge=1\),\s*db:\s*Session\s*=\s*Depends\(get_db\),\s*current_user:\s*User\s*=\s*Depends\(get_current_user\)\s*\):"
    repl_list = """def list_exchanges(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    company_id: Optional[int] = Query(None),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):"""
    c, n_list = re.subn(pattern_list, repl_list, c)
    print("Replaced list_exchanges:", n_list)

    # Fix create_exchange
    pattern_create = r"def create_exchange\s*\(\s*exchange_in:\s*ExchangeCreate,\s*db:\s*Session\s*=\s*Depends\(get_db\),\s*current_user:\s*User\s*=\s*Depends\(get_current_user\)\s*\):"
    repl_create = """def create_exchange(
    exchange_in: ExchangeCreate,
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):"""
    c, n_create = re.subn(pattern_create, repl_create, c)
    print("Replaced create_exchange:", n_create)

    with open(p, "w", encoding="utf-8") as f:
        f.write(c)

if __name__ == "__main__":
    fix_purchases()
    fix_exchanges()
