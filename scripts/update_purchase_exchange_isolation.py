import os
import re

def update_exchange_model():
    p = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\models\exchange.py"
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()
    if "company_id:" not in c:
        c = c.replace(
            "store_id: Mapped[Optional[int]] = mapped_column(Integer, default=1, index=True)",
            'company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True, default=1, index=True)\n    store_id: Mapped[Optional[int]] = mapped_column(Integer, default=1, index=True)'
        )
        with open(p, "w", encoding="utf-8") as f:
            f.write(c)
        print("Updated exchange model")
    else:
        print("Exchange model already has company_id")

def update_purchases_api():
    p = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\purchases.py"
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Add Header, or_ import if missing
    if "from sqlalchemy import or_" not in c:
        c = c.replace("from sqlalchemy.orm import Session", "from sqlalchemy.orm import Session\nfrom sqlalchemy import or_")
    if "Header" not in c:
        c = c.replace("from fastapi import APIRouter, Depends, HTTPException, status, Request, Query",
                      "from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Header")

    # 2. Update get_unified_purchases_history
    target_hist = """def get_unified_purchases_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:"""
    
    repl_hist = """def get_unified_purchases_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    company_id: Optional[int] = Query(None),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:"""

    c = c.replace(target_hist, repl_hist)

    # In body of get_unified_purchases_history, filter by company_id
    old_filter = "query = db.query(Purchase).filter(Purchase.store_id == store_id)"
    new_filter = """query = db.query(Purchase).filter(Purchase.store_id == store_id)
    active_company = company_id
    if not active_company and x_company_id and x_company_id.isdigit():
        active_company = int(x_company_id)
    if not active_company:
        active_company = 1
    if active_company == 1:
        query = query.filter(or_(Purchase.company_id == 1, Purchase.company_id.is_(None)))
    else:
        query = query.filter(Purchase.company_id == active_company)"""
    
    c = c.replace(old_filter, new_filter, 1)

    # 3. Update create_unified_purchase to take x_company_id and set company_id
    target_create = """def create_unified_purchase(
    purchase_in: UnifiedPurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:"""
    
    repl_create = """def create_unified_purchase(
    purchase_in: UnifiedPurchaseCreate,
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:"""

    c = c.replace(target_create, repl_create)

    # In body of create_unified_purchase, set company_id
    target_purchase_inst = """    db_purchase = Purchase(
        store_id=store_id,"""

    repl_purchase_inst = """    target_company = getattr(purchase_in, "company_id", None)
    if not target_company and x_company_id and x_company_id.isdigit():
        target_company = int(x_company_id)
    if not target_company:
        target_company = 1

    db_purchase = Purchase(
        store_id=store_id,
        company_id=target_company,"""

    c = c.replace(target_purchase_inst, repl_purchase_inst, 1)

    with open(p, "w", encoding="utf-8") as f:
        f.write(c)
    print("Updated purchases.py for company isolation")

def update_exchanges_api():
    p = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\exchanges.py"
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()

    # Imports
    if "from sqlalchemy import or_" not in c:
        c = c.replace("from sqlalchemy.orm import Session", "from sqlalchemy.orm import Session\nfrom sqlalchemy import or_")
    if "Header" not in c:
        c = c.replace("from fastapi import APIRouter, Depends, HTTPException, Query, status",
                      "from fastapi import APIRouter, Depends, HTTPException, Query, status, Header")

    # 1. Update list_exchanges
    target_list = """def list_exchanges(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):"""

    repl_list = """def list_exchanges(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    company_id: Optional[int] = Query(None),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):"""

    c = c.replace(target_list, repl_list)

    old_filter = "query = db.query(Exchange).filter(Exchange.store_id == store_id)"
    new_filter = """query = db.query(Exchange).filter(Exchange.store_id == store_id)
    active_company = company_id
    if not active_company and x_company_id and x_company_id.isdigit():
        active_company = int(x_company_id)
    if not active_company:
        active_company = 1
    if active_company == 1:
        query = query.filter(or_(Exchange.company_id == 1, Exchange.company_id.is_(None)))
    else:
        query = query.filter(Exchange.company_id == active_company)"""

    c = c.replace(old_filter, new_filter, 1)

    # 2. Update create_exchange
    target_create = """def create_exchange(
    exchange_in: ExchangeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):"""

    repl_create = """def create_exchange(
    exchange_in: ExchangeCreate,
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):"""

    c = c.replace(target_create, repl_create)

    target_exchange_inst = """    db_exchange = Exchange(
        store_id=store_id,"""

    repl_exchange_inst = """    target_company = getattr(exchange_in, "company_id", None)
    if not target_company and x_company_id and x_company_id.isdigit():
        target_company = int(x_company_id)
    if not target_company:
        target_company = 1

    db_exchange = Exchange(
        store_id=store_id,
        company_id=target_company,"""

    c = c.replace(target_exchange_inst, repl_exchange_inst, 1)

    with open(p, "w", encoding="utf-8") as f:
        f.write(c)
    print("Updated exchanges.py for company isolation")

def update_schemas():
    p_pur = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\schemas\purchases.py"
    with open(p_pur, "r", encoding="utf-8") as f:
        cp = f.read()
    if "company_id: Optional[int] = 1" not in cp:
        cp = cp.replace("class UnifiedPurchaseCreate(BaseModel):", "class UnifiedPurchaseCreate(BaseModel):\n    company_id: Optional[int] = 1")
        with open(p_pur, "w", encoding="utf-8") as f:
            f.write(cp)
        print("Updated purchases schema with company_id")

    p_ex = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\schemas\exchange.py"
    with open(p_ex, "r", encoding="utf-8") as f:
        ce = f.read()
    if "company_id: Optional[int] = 1" not in ce:
        ce = ce.replace("class ExchangeCreate(BaseModel):", "class ExchangeCreate(BaseModel):\n    company_id: Optional[int] = 1")
        with open(p_ex, "w", encoding="utf-8") as f:
            f.write(ce)
        print("Updated exchange schema with company_id")

if __name__ == "__main__":
    update_exchange_model()
    update_purchases_api()
    update_exchanges_api()
    update_schemas()
