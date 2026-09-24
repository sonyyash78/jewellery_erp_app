from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime
from app.api.dependencies import get_db, get_current_user
from app.models.invoice import Invoice
from app.models.purchase import Purchase
from app.models.stock_item import StockItem
from app.models.customer import Customer
from app.models.seller import Seller

router = APIRouter(dependencies=[Depends(get_current_user)])

class AIQuery(BaseModel):
    prompt: str

@router.post("/chat")
def process_ai_chat(query: AIQuery, db: Session = Depends(get_db)):
    prompt = query.prompt.lower().strip()
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. Today's Sales
    if "today" in prompt and "sale" in prompt:
        sales = db.query(func.sum(Invoice.grand_total)).filter(Invoice.invoice_date >= start_of_day).scalar() or 0
        return {"response": f"**Today's Total Sales** amount to **₹{sales:,.2f}**."}

    # 2. Today's Purchases
    if "today" in prompt and "purchase" in prompt:
        purchases = db.query(func.sum(Purchase.grand_total)).filter(Purchase.created_at >= start_of_day).scalar() or 0
        return {"response": f"**Today's Total Purchases** amount to **₹{purchases:,.2f}**."}

    # 3. Top Customers
    if "top" in prompt and "customer" in prompt:
        # Sort by those who bought most? Or just list top 5
        customers = db.query(Customer).order_by(Customer.id.desc()).limit(5).all()
        lines = [f"- **{c.first_name} {c.last_name or ''}**: Ph: {c.phone_number}" for c in customers]
        return {"response": "**Your Recent Customers:**\n" + "\n".join(lines)}

    # 4. Low Stock
    if "low" in prompt and "stock" in prompt:
        # Since weight is dynamic, let's just count total Active items
        active = db.query(StockItem).filter(StockItem.status == 'Active').count()
        if active < 10:
            return {"response": f"⚠️ **Low Stock Alert**: You only have **{active}** active items in inventory!"}
        return {"response": f"✅ Your inventory is healthy with **{active}** active items ready to sell."}

    # 5. Search Customer
    if "search customer" in prompt:
        name = prompt.replace("search customer", "").strip()
        if not name:
            return {"response": "Please provide a name, e.g., 'search customer Rahul'"}
        c = db.query(Customer).filter(Customer.first_name.ilike(f"%{name}%")).first()
        if c:
            return {"response": f"Found **{c.first_name} {c.last_name or ''}**\nPhone: {c.phone_number}\nOutstanding: ₹{c.outstanding_balance or 0}"}
        return {"response": f"Could not find any customer matching '{name}'."}

    # 6. Default Fallback
    return {
        "response": "I am your Jewellery ERP AI Assistant. Try asking me:\n- *What are today's sales?*\n- *Show me low stock*\n- *Search customer [name]*"
    }
