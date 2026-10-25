import re
import logging
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, String
from pydantic import BaseModel
import httpx

from app.api.dependencies import get_db, get_current_user, require_tenant_id
from app.core.config import settings
from app.models.user import User
from app.models.invoice import Invoice
from app.models.purchase import Purchase
from app.models.stock_item import StockItem
from app.models.crm import Customer, Supplier
from app.models.exchange import Exchange
from app.models.accounting import Expense
from app.models.gold_rate import GoldRate
from app.models.silver_rate import SilverRate
from app.models.purity import Purity
from app.models.metal_type import MetalType

router = APIRouter(dependencies=[Depends(get_current_user)])
logger = logging.getLogger(__name__)


class ChatHistoryItem(BaseModel):
    role: str
    text: str


class AIQuery(BaseModel):
    prompt: str
    history: Optional[List[ChatHistoryItem]] = None


def _format_currency(amount: float) -> str:
    """Formats float as Indian Rupee string."""
    return f"₹{amount:,.2f}"


def _mask_phone(phone: str | None) -> str:
    """Mask phone number to protect customer PII when sending to external LLM."""
    if not phone:
        return ""
    clean = str(phone).strip()
    if len(clean) >= 6:
        return "*" * (len(clean) - 4) + clean[-4:]
    return "****"


def _get_time_boundaries():
    now = datetime.now()
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_yesterday = start_today - timedelta(days=1)
    end_yesterday = start_today
    start_week = start_today - timedelta(days=now.weekday())  # Monday start
    start_last_week = start_week - timedelta(days=7)
    end_last_week = start_week
    start_7_days = start_today - timedelta(days=7)
    start_30_days = start_today - timedelta(days=30)
    start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_prev_month = start_month - timedelta(days=1)
    start_prev_month = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_prev_month = start_month
    return (
        now,
        start_today,
        start_yesterday,
        end_yesterday,
        start_week,
        start_last_week,
        end_last_week,
        start_7_days,
        start_30_days,
        start_month,
        start_prev_month,
        end_prev_month,
    )


def _build_store_context(db: Session, store_id: int, prompt_lower: str) -> str:
    """
    Constructs a real-time, tenant-isolated snapshot of the store's key metrics.
    Injected into Gemini system context so generated responses use real, factual data.
    """
    (
        now,
        start_today,
        start_yesterday,
        end_yesterday,
        start_week,
        start_last_week,
        end_last_week,
        start_7_days,
        start_30_days,
        start_month,
        start_prev_month,
        end_prev_month,
    ) = _get_time_boundaries()
    context_parts = []
    context_parts.append(f"Current Date & Time: {now.strftime('%d %B %Y, %I:%M %p')}")

    # 1. Live Metal Rates
    try:
        gold_purities = db.query(Purity).join(MetalType).filter(MetalType.name == "Gold").all()
        silver_purities = db.query(Purity).join(MetalType).filter(MetalType.name == "Silver").all()
        rates_info = []
        for p in gold_purities:
            rate_obj = db.query(GoldRate).filter(GoldRate.purity_id == p.id).order_by(desc(GoldRate.effective_datetime)).first()
            if rate_obj and rate_obj.rate_per_gram:
                r = float(rate_obj.rate_per_gram)
                rates_info.append(f"Gold {p.karat_name}: ₹{r:,.2f}/g (₹{r*10:,.2f} per 10g)")
        for p in silver_purities:
            rate_obj = db.query(SilverRate).filter(SilverRate.purity_id == p.id).order_by(desc(SilverRate.effective_datetime)).first()
            if rate_obj and rate_obj.rate_per_gram:
                r = float(rate_obj.rate_per_gram)
                rates_info.append(f"Silver {p.karat_name}: ₹{r:,.2f}/g (₹{r*1000:,.2f} per kg)")
        if rates_info:
            context_parts.append("Store Live Metal Rates:\n- " + "\n- ".join(rates_info))
        else:
            context_parts.append("Store Live Metal Rates: Not yet configured today in store.")
    except Exception as e:
        logger.debug(f"Error building rates context: {e}")

    # 2. Sales Summary (Today, Yesterday, Last 7 Days, This Week, Last Week, This Month, Last 30 Days)
    try:
        today_sales = db.query(func.sum(Invoice.grand_total)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_today).scalar() or 0.0
        today_cash = db.query(func.sum(Invoice.cash_received)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_today).scalar() or 0.0
        today_bills = db.query(func.count(Invoice.id)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_today).scalar() or 0
        today_balance = db.query(func.sum(Invoice.balance_amount)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_today).scalar() or 0.0
        today_metal_val = db.query(func.sum(Invoice.metal_received_value)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_today).scalar() or 0.0

        yesterday_sales = db.query(func.sum(Invoice.grand_total)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_yesterday, Invoice.invoice_date < end_yesterday).scalar() or 0.0
        yesterday_bills = db.query(func.count(Invoice.id)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_yesterday, Invoice.invoice_date < end_yesterday).scalar() or 0

        # Previous 7 Days Total & Day-by-Day Breakdown
        sales_7d = db.query(func.sum(Invoice.grand_total)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_7_days).scalar() or 0.0
        bills_7d = db.query(func.count(Invoice.id)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_7_days).scalar() or 0
        cash_7d = db.query(func.sum(Invoice.cash_received)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_7_days).scalar() or 0.0

        daily_7d_rows = db.query(
            func.date(Invoice.invoice_date).label("d"),
            func.sum(Invoice.grand_total).label("amt"),
            func.count(Invoice.id).label("cnt")
        ).filter(
            Invoice.store_id == store_id,
            Invoice.invoice_date >= start_7_days
        ).group_by(func.date(Invoice.invoice_date)).order_by(desc("d")).all()
        daily_breakdown_str = "; ".join(f"{r.d}: {_format_currency(float(r.amt))} ({r.cnt} bills)" for r in daily_7d_rows)

        # This Week (from Monday)
        this_week_sales = db.query(func.sum(Invoice.grand_total)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_week).scalar() or 0.0
        this_week_bills = db.query(func.count(Invoice.id)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_week).scalar() or 0

        # Last Week (Mon-Sun)
        last_week_sales = db.query(func.sum(Invoice.grand_total)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_last_week, Invoice.invoice_date < end_last_week).scalar() or 0.0
        last_week_bills = db.query(func.count(Invoice.id)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_last_week, Invoice.invoice_date < end_last_week).scalar() or 0

        # This Month
        month_sales = db.query(func.sum(Invoice.grand_total)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_month).scalar() or 0.0
        month_bills = db.query(func.count(Invoice.id)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_month).scalar() or 0

        # Previous 30 Days
        sales_30d = db.query(func.sum(Invoice.grand_total)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_30_days).scalar() or 0.0
        bills_30d = db.query(func.count(Invoice.id)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= start_30_days).scalar() or 0

        # Custom N Days if requested in prompt (e.g. "prev 10 days", "last 15 din")
        custom_n_str = ""
        n_match = re.search(r"(?:last|prev|previous|pichle|past)?\s*(\d+)\s*(?:days?|din)", prompt_lower)
        if n_match:
            n_days = int(n_match.group(1))
            if n_days not in [1, 7, 30]:
                custom_start = start_today - timedelta(days=n_days)
                c_sales = db.query(func.sum(Invoice.grand_total)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= custom_start).scalar() or 0.0
                c_bills = db.query(func.count(Invoice.id)).filter(Invoice.store_id == store_id, Invoice.invoice_date >= custom_start).scalar() or 0
                custom_n_str = f"\n- Custom Requested Last {n_days} Days: {_format_currency(float(c_sales))} across {c_bills} bills"

        context_parts.append(
            f"Sales Performance Across Time Periods:\n"
            f"- Today's Sales: {_format_currency(float(today_sales))} across {today_bills} bills (Cash/UPI: {_format_currency(float(today_cash))}, Old Metal Value: {_format_currency(float(today_metal_val))}, Pending Due on today's bills: {_format_currency(float(today_balance))})\n"
            f"- Yesterday's Sales: {_format_currency(float(yesterday_sales))} across {yesterday_bills} bills\n"
            f"- Previous 7 Days Total (Last 7 Days): {_format_currency(float(sales_7d))} across {bills_7d} bills (Cash/UPI: {_format_currency(float(cash_7d))})\n"
            f"  * Day-by-Day Breakdown (Last 7 Days): {daily_breakdown_str if daily_breakdown_str else 'No sales recorded in last 7 days'}\n"
            f"- This Week's Sales (from Monday): {_format_currency(float(this_week_sales))} across {this_week_bills} bills\n"
            f"- Last Week's Sales (Mon-Sun): {_format_currency(float(last_week_sales))} across {last_week_bills} bills\n"
            f"- This Month's Sales ({now.strftime('%B %Y')}): {_format_currency(float(month_sales))} across {month_bills} bills\n"
            f"- Previous 30 Days Total: {_format_currency(float(sales_30d))} across {bills_30d} bills"
            f"{custom_n_str}"
        )
    except Exception as e:
        logger.debug(f"Error building sales context: {e}")

    # 3. Stock / Inventory
    try:
        total_items = db.query(StockItem).filter(StockItem.store_id == store_id, StockItem.status.in_(["Available", "Active"])).count()
        gold_items = db.query(StockItem).filter(StockItem.store_id == store_id, StockItem.status.in_(["Available", "Active"]), StockItem.metal.ilike("%gold%")).all()
        silver_items = db.query(StockItem).filter(StockItem.store_id == store_id, StockItem.status.in_(["Available", "Active"]), StockItem.metal.ilike("%silver%")).all()
        gold_cnt = len(gold_items)
        gold_gross = sum(float(i.gross_weight or 0) for i in gold_items)
        gold_net = sum(float(i.net_weight or 0) for i in gold_items)
        silver_cnt = len(silver_items)
        silver_gross = sum(float(i.gross_weight or 0) for i in silver_items)
        silver_net = sum(float(i.net_weight or 0) for i in silver_items)
        categories = db.query(StockItem.category, func.count(StockItem.id)).filter(StockItem.store_id == store_id, StockItem.status.in_(["Available", "Active"])).group_by(StockItem.category).order_by(desc(func.count(StockItem.id))).limit(5).all()
        cat_str = ", ".join(f"{cat or 'General'}: {cnt} items" for cat, cnt in categories)

        context_parts.append(
            f"Inventory Stock in Store:\n"
            f"- Total Ready Items: {total_items}\n"
            f"- Gold Stock: {gold_cnt} items, Gross Weight: {gold_gross:.3f}g, Net Weight: {gold_net:.3f}g\n"
            f"- Silver Stock: {silver_cnt} items, Gross Weight: {silver_gross:.3f}g, Net Weight: {silver_net:.3f}g\n"
            f"- Top Categories: {cat_str if cat_str else 'None'}"
        )
    except Exception as e:
        logger.debug(f"Error building stock context: {e}")

    # 4. Market Udhari / Receivables
    try:
        total_market_due = db.query(func.sum(Customer.outstanding_balance)).filter(Customer.store_id == store_id, Customer.is_deleted == False).scalar() or 0.0
        total_due_count = db.query(func.count(Customer.id)).filter(Customer.store_id == store_id, Customer.outstanding_balance > 0, Customer.is_deleted == False).scalar() or 0
        top_due_customers = db.query(Customer).filter(Customer.store_id == store_id, Customer.outstanding_balance > 0, Customer.is_deleted == False).order_by(desc(Customer.outstanding_balance)).limit(5).all()
        due_lines = [f"{c.first_name} {c.last_name or ''} (Phone: {_mask_phone(c.phone_number)}): {_format_currency(float(c.outstanding_balance))}" for c in top_due_customers]
        context_parts.append(
            f"Market Udhari (Customer Receivables):\n"
            f"- Total Outstanding Dues: {_format_currency(float(total_market_due))} ({total_due_count} customers have pending balance)\n"
            f"- Top 5 Pending Customers: {'; '.join(due_lines) if due_lines else 'None (All accounts cleared)'}"
        )
    except Exception as e:
        logger.debug(f"Error building udhari context: {e}")

    # 5. Expenses
    try:
        today_exp = db.query(func.sum(Expense.amount)).filter(Expense.store_id == store_id, Expense.expense_date >= start_today.date()).scalar() or 0.0
        month_exp = db.query(func.sum(Expense.amount)).filter(Expense.store_id == store_id, Expense.expense_date >= start_month.date()).scalar() or 0.0
        context_parts.append(f"Shop Expenses: Today: {_format_currency(float(today_exp))}, This Month: {_format_currency(float(month_exp))}")
    except Exception as e:
        logger.debug(f"Error building expenses context: {e}")

    # 6. Supplier Dues
    try:
        total_supp_due = db.query(func.sum(Supplier.outstanding_balance)).filter(Supplier.store_id == store_id, Supplier.is_deleted == False).scalar() or 0.0
        top_suppliers = db.query(Supplier).filter(Supplier.store_id == store_id, Supplier.outstanding_balance > 0, Supplier.is_deleted == False).order_by(desc(Supplier.outstanding_balance)).limit(4).all()
        supp_lines = [f"{s.name} (Mobile: {_mask_phone(s.mobile)}): {_format_currency(float(s.outstanding_balance))}" for s in top_suppliers]
        context_parts.append(f"Supplier / Karigar Payables: Total: {_format_currency(float(total_supp_due))}, Top Dues: {'; '.join(supp_lines) if supp_lines else 'None'}")
    except Exception as e:
        logger.debug(f"Error building supplier context: {e}")

    # 7. Old Gold Exchanges Today
    try:
        today_exchanges = db.query(Exchange).filter(Exchange.store_id == store_id, Exchange.exchange_date >= start_today).all()
        ex_val = sum(float(e.total_old_value or 0) for e in today_exchanges)
        ex_gold_wt = sum(float(e.gold_balance_metal_weight or 0) for e in today_exchanges)
        ex_silver_wt = sum(float(e.silver_balance_metal_weight or 0) for e in today_exchanges)
        context_parts.append(f"Old Gold / Exchange Today: {len(today_exchanges)} exchanges, Total Old Metal Value: {_format_currency(ex_val)}, Gold Received: {ex_gold_wt:.3f}g, Silver Received: {ex_silver_wt:.3f}g")
    except Exception as e:
        logger.debug(f"Error building exchange context: {e}")

    # 8. Specific Customer Lookup if mentioned
    try:
        phone_match = re.search(r"\b\d{10}\b", prompt_lower)
        clean_cust_search = prompt_lower.replace("customer", "").replace("grahak", "").replace("search", "").strip()
        if phone_match or (len(clean_cust_search) >= 3 and any(w in prompt_lower for w in ["customer", "grahak", "phone", "profile"])):
            cust_q = db.query(Customer).filter(Customer.store_id == store_id, Customer.is_deleted == False)
            if phone_match:
                c = cust_q.filter(Customer.phone_number.contains(phone_match.group(0))).first()
            else:
                c = cust_q.filter(or_(Customer.first_name.ilike(f"%{clean_cust_search}%"), Customer.last_name.ilike(f"%{clean_cust_search}%"))).first()
            if c:
                bill_cnt = db.query(func.count(Invoice.id)).filter(Invoice.store_id == store_id, Invoice.customer_id == c.id).scalar() or 0
                context_parts.append(
                    f"Searched Customer Profile Found:\n"
                    f"- Full Name: {c.first_name} {c.last_name or ''}\n"
                    f"- Phone: {_mask_phone(c.phone_number)}\n"
                    f"- Address: {c.city or 'N/A'}, {c.state or ''}\n"
                    f"- Pending Udhari Balance: {_format_currency(float(c.outstanding_balance or 0))}\n"
                    f"- Fine Gold Due: {float(c.fine_gold_balance or 0):.3f}g\n"
                    f"- Total Invoices: {bill_cnt} bills"
                )
    except Exception as e:
        logger.debug(f"Error looking up customer: {e}")

    # 9. Specific Invoice Lookup if mentioned
    try:
        inv_match = re.search(r"(?:inv-?|bill-?|#)\s*([0-9a-zA-Z-]+)", prompt_lower)
        if inv_match:
            term = inv_match.group(1)
            inv = db.query(Invoice).filter(
                Invoice.store_id == store_id,
                or_(Invoice.invoice_number.ilike(f"%{term}%"), func.cast(Invoice.id, String(50)) == term)
            ).first()
            if inv:
                c_name = "Walk-in Customer"
                if inv.customer_id:
                    cust = db.query(Customer).filter_by(id=inv.customer_id).first()
                    if cust:
                        c_name = f"{cust.first_name} {cust.last_name or ''}".strip()
                date_s = inv.invoice_date.strftime("%d %b %Y, %I:%M %p") if inv.invoice_date else "N/A"
                st = inv.status.value if hasattr(inv.status, 'value') else (inv.status or 'Completed')
                context_parts.append(
                    f"Searched Invoice Found:\n"
                    f"- Invoice Number: {inv.invoice_number}\n"
                    f"- Customer: {c_name}\n"
                    f"- Date: {date_s}\n"
                    f"- Grand Total: {_format_currency(float(inv.grand_total))}\n"
                    f"- Cash/Digital Paid: {_format_currency(float(inv.cash_received or 0))}\n"
                    f"- Balance Due: {_format_currency(float(inv.balance_amount or 0))}\n"
                    f"- Status: {st}"
                )
    except Exception as e:
        logger.debug(f"Error looking up invoice: {e}")

    return "\n\n".join(context_parts)


def get_effective_gemini_key(db: Optional[Session] = None) -> Optional[str]:
    """
    Retrieves configured Gemini API key with resolution cascade:
    1. Memory settings (settings.GEMINI_API_KEY)
    2. OS Environment variable (GEMINI_API_KEY)
    3. Database system_settings table
    4. JewelleryERP_Data/.env file
    """
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip() and not settings.GEMINI_API_KEY.strip().startswith("your-gemini"):
        return settings.GEMINI_API_KEY.strip()

    env_k = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if env_k and not env_k.startswith("your-gemini"):
        return env_k

    if db:
        try:
            from app.models.system_setting import SystemSetting
            setting = db.query(SystemSetting).filter(SystemSetting.setting_key == "GEMINI_API_KEY").first()
            if setting and setting.setting_value and setting.setting_value.strip():
                k = setting.setting_value.strip()
                if not k.startswith("your-gemini"):
                    return k
        except Exception:
            pass

    try:
        from app.core.config import DATA_ENV
        if DATA_ENV.exists():
            with open(DATA_ENV, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        k = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        if k and not k.startswith("your-gemini"):
                            return k
    except Exception:
        pass

    return None


def call_gemini_api(
    prompt: str,
    context: str,
    history: Optional[List[Dict[str, str]]] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Optional[str]:
    """
    Directly invokes Google Gemini API via REST endpoint with real-time store context.
    Returns natural language response string or None if unconfigured/failed.
    """
    key = api_key or get_effective_gemini_key()
    if not key or not key.strip() or key.strip().startswith("your-gemini"):
        return None

    model_name = model or settings.GEMINI_MODEL or "gemini-2.5-flash"
    candidate_models = [model_name]
    for m in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]:
        if m not in candidate_models:
            candidate_models.append(m)

    system_instruction = (
        "You are the intelligent, highly capable AI Business Copilot for Saideep Jewellery ERP.\n"
        "You are having a direct conversation with the jewellery store owner or staff.\n\n"
        "COMMUNICATION RULES:\n"
        "1. Speak naturally, warmly, and fluently in Hindi, Hinglish, or English. Match the language and tone of the user's prompt.\n"
        "2. Do NOT use fixed, rigid statements or robotic canned templates. Formulate dynamic, helpful, and natural sentences.\n"
        "3. Always use the REAL-TIME LIVE STORE DATA provided below to answer business questions accurately.\n"
        "4. Format summaries clearly using bold headers, neat bullet points, and Rupee symbols (₹).\n"
        "5. For jewellery pricing calculations (e.g., '10g 22k rate 72000' or custom making charges), explain the breakdown: Base Metal Cost + Making + 3% GST.\n"
        "6. If the user asks general questions about hallmarking (BIS 6-digit HUID), gold purity (24K/22K/18K/14K), gold investment, market trends, or store advice, answer knowledgeably and helpfully.\n"
        "7. Keep messages concise and formatted for mobile and desktop chat panels.\n\n"
        "--- REAL-TIME LIVE STORE DATA (TENANT-ISOLATED SNAPSHOT) ---\n"
        f"{context}"
    )

    contents = []
    # Include recent conversation turns if present
    if history:
        for turn in history[-8:]:
            role = turn.get("role", "")
            text = turn.get("text", "")
            if not text:
                continue
            gemini_role = "user" if role == "user" else "model"
            contents.append({
                "role": gemini_role,
                "parts": [{"text": text}]
            })

    # Append current user prompt
    contents.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })

    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1200
        }
    }

    headers = {
        "x-goog-api-key": key.strip(),
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            for current_model in candidate_models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent"
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
                elif resp.status_code == 404:
                    logger.info(f"Model {current_model} not found, trying next candidate model...")
                    continue
                else:
                    logger.warning(f"Gemini API returned status {resp.status_code} on {current_model}: {resp.text[:200]}")
                    break
    except Exception as e:
        logger.warning(f"Gemini API request failed: {str(e)}")

    return None


def _local_rule_fallback(prompt: str, store_id: int, db: Session) -> Dict[str, Any]:
    """
    High-speed deterministic fallback engine used when GEMINI_API_KEY is not configured
    or if network/quota is temporarily unavailable.
    """
    (
        now,
        start_today,
        start_yesterday,
        end_yesterday,
        start_week,
        start_last_week,
        end_last_week,
        start_7_days,
        start_30_days,
        start_month,
        start_prev_month,
        end_prev_month,
    ) = _get_time_boundaries()

    # 1. Greetings & Help
    greeting_triggers = ["hello", "hi", "namaste", "pranam", "kya kar sakte ho", "help", "options", "commands"]
    if any(re.search(rf"\b{re.escape(g)}\b", prompt) for g in greeting_triggers) and len(prompt.split()) <= 4:
        return {
            "response": (
                "🙏 **Namaste! Main aapka Saideep Jewellery ERP AI Assistant hoon.**\n\n"
                "Aap mujhse store ke business data ke baare me Hindi, Hinglish ya English me pooch sakte hain:\n\n"
                "📊 **Sales (Bikri):**\n"
                "- *Aaj ki sale kitni hui?*\n"
                "- *Pichhle 7 din ki sale dikhao*\n"
                "- *Is mahine ki total sale dikhao*\n"
                "- *Kal ki sale kitni thi?*\n\n"
                "👥 **Udhari & Khata (Dues):**\n"
                "- *Kiske paise baaki hain? (Top udhari)*\n"
                "- *Total market me kitna balance baaki hai?*\n"
                "- *Customer search: Ramesh Kumar*\n\n"
                "⚖️ **Stock & Inventory:**\n"
                "- *Gold aur silver stock kitna bacha hai?*\n"
                "- *Bangles ya Ring ka kitna stock hai?*\n\n"
                "💰 **Rates & Bhav:**\n"
                "- *Aaj ka gold aur silver rate kya hai?*\n\n"
                "🧾 **Invoices & Bills:**\n"
                "- *Aaj kitne bill bane?*\n"
                "- *Bill search: INV-1001*\n\n"
                "💸 **Kharcha & Suppliers:**\n"
                "- *Aaj ka dukan ka kharcha kitna hua?*\n"
                "- *Supplier ko kitne paise dene hain?*\n\n"
                "🔄 **Exchange:**\n"
                "- *Purana sona kitna aaya (Exchange summary)?*"
            ),
            "source": "local"
        }

    # 2. Metal Rates / Bhav
    rate_triggers = ["rate", "rates", "bhav", "sona ka rate", "gold rate", "silver rate", "chandi ka bhav", "aaj ka rate"]
    if any(k in prompt for k in rate_triggers) and not any(k in prompt for k in ["sale", "bikri", "purchase"]) and not re.search(r"\d+\s*(?:g|gram|gms)", prompt):
        gold_purities = db.query(Purity).join(MetalType).filter(MetalType.name == "Gold").all()
        silver_purities = db.query(Purity).join(MetalType).filter(MetalType.name == "Silver").all()

        rate_lines = []
        for p in gold_purities:
            rate_obj = db.query(GoldRate).filter(GoldRate.purity_id == p.id).order_by(desc(GoldRate.effective_datetime)).first()
            if rate_obj and rate_obj.rate_per_gram:
                r = float(rate_obj.rate_per_gram)
                rate_lines.append(f"- **Gold {p.karat_name}**: ₹{r:,.2f}/g (₹{r*10:,.2f} per 10g)")

        for p in silver_purities:
            rate_obj = db.query(SilverRate).filter(SilverRate.purity_id == p.id).order_by(desc(SilverRate.effective_datetime)).first()
            if rate_obj and rate_obj.rate_per_gram:
                r = float(rate_obj.rate_per_gram)
                rate_lines.append(f"- **Silver {p.karat_name}**: ₹{r:,.2f}/g (₹{r*1000:,.2f} per kg)")

        if rate_lines:
            return {
                "response": "💰 **Current Metal Rates in Store:**\n\n" + "\n".join(rate_lines) + "\n\n*(Rates can be updated in Live Metal Rates module)*",
                "source": "local"
            }
        return {
            "response": "⚠️ Store me abhi metal rates set nahi hain. Aap **Live Rates** section me jaakar update kar sakte hain.",
            "source": "local"
        }

    # 3. Sales Analytics
    sale_triggers = ["sale", "sales", "bikri", "revenue", "collection", "turnover", "kamai", "becha"]
    if any(k in prompt for k in sale_triggers) or (("aaj" in prompt or "today" in prompt) and "bill" in prompt):
        is_yesterday = "yesterday" in prompt or "kal" in prompt
        is_7_days = any(k in prompt for k in ["7 day", "7 days", "7 din", "seven day", "last 7", "prev 7"])
        is_30_days = any(k in prompt for k in ["30 day", "30 days", "30 din", "thirty day", "last 30", "prev 30"])
        is_last_week = "last week" in prompt or "prev week" in prompt or "pichle hafte" in prompt or "pichla hafta" in prompt
        is_last_month = "last month" in prompt or "prev month" in prompt or "pichle mahine" in prompt or "pichla mahina" in prompt
        is_month = "month" in prompt or "mahina" in prompt or "mahine" in prompt
        is_week = "week" in prompt or "hafte" in prompt or "hafta" in prompt
        n_match = re.search(r"(?:last|prev|previous|pichle|past)?\s*(\d+)\s*(?:days?|din)", prompt)

        if is_yesterday:
            window_start = start_yesterday
            window_end = end_yesterday
            period_label = "Kal Ki Sales (Yesterday)"
        elif is_7_days:
            window_start = start_7_days
            window_end = None
            period_label = "Pichhle 7 Din Ki Sales (Last 7 Days)"
        elif is_30_days:
            window_start = start_30_days
            window_end = None
            period_label = "Pichhle 30 Din Ki Sales (Last 30 Days)"
        elif n_match and int(n_match.group(1)) not in [1, 7, 30]:
            n_val = int(n_match.group(1))
            window_start = start_today - timedelta(days=n_val)
            window_end = None
            period_label = f"Pichhle {n_val} Din Ki Sales (Last {n_val} Days)"
        elif is_last_week:
            window_start = start_last_week
            window_end = end_last_week
            period_label = "Pichhle Hafte Ki Sales (Last Week)"
        elif is_last_month:
            window_start = start_prev_month
            window_end = end_prev_month
            period_label = "Pichhle Mahine Ki Sales (Last Month)"
        elif is_month:
            window_start = start_month
            window_end = None
            period_label = "Is Mahine Ki Sales (This Month)"
        elif is_week:
            window_start = start_week
            window_end = None
            period_label = "Is Hafte Ki Sales (This Week)"
        else:
            window_start = start_today
            window_end = None
            period_label = "Aaj Ki Sales (Today)"

        query_filter = [Invoice.store_id == store_id, Invoice.invoice_date >= window_start]
        if window_end:
            query_filter.append(Invoice.invoice_date < window_end)

        total_sales = db.query(func.sum(Invoice.grand_total)).filter(*query_filter).scalar() or 0.0
        total_cash = db.query(func.sum(Invoice.cash_received)).filter(*query_filter).scalar() or 0.0
        total_metal_val = db.query(func.sum(Invoice.metal_received_value)).filter(*query_filter).scalar() or 0.0
        total_balance = db.query(func.sum(Invoice.balance_amount)).filter(*query_filter).scalar() or 0.0
        bill_count = db.query(func.count(Invoice.id)).filter(*query_filter).scalar() or 0
        avg_bill = (float(total_sales) / bill_count) if bill_count > 0 else 0.0

        res_msg = (
            f"📊 **{period_label}:**\n\n"
            f"- 💰 **Total Sales Amount:** {_format_currency(float(total_sales))}\n"
            f"- 🧾 **Total Bills Created:** **{bill_count}** bills\n"
            f"- 💵 **Cash / Digital Received:** {_format_currency(float(total_cash))}\n"
        )
        if total_metal_val > 0:
            res_msg += f"- 🪙 **Old Metal Received Value:** {_format_currency(float(total_metal_val))}\n"
        if total_balance > 0:
            res_msg += f"- ⏳ **Pending Balance / Udhari on Bills:** {_format_currency(float(total_balance))}\n"
        if bill_count > 0:
            res_msg += f"- 📈 **Average Bill Size:** {_format_currency(avg_bill)}\n"

        if is_7_days or (n_match and int(n_match.group(1)) <= 15):
            daily_rows = db.query(
                func.date(Invoice.invoice_date).label("d"),
                func.sum(Invoice.grand_total).label("amt"),
                func.count(Invoice.id).label("cnt")
            ).filter(*query_filter).group_by(func.date(Invoice.invoice_date)).order_by(desc("d")).all()
            if daily_rows:
                res_msg += "\n**📅 Day-by-Day Hisaab:**\n"
                for dr in daily_rows:
                    res_msg += f"- **{dr.d}**: {_format_currency(float(dr.amt))} ({dr.cnt} bills)\n"

        return {"response": res_msg, "source": "local"}

    # 4. Udhari / Khata
    udhari_triggers = ["udhari", "udhar", "khata", "pending", "baaki", "baki", "due", "dues", "balance", "kiske paise", "market"]
    if any(k in prompt for k in udhari_triggers) and not any(k in prompt for k in ["supplier", "purchase"]):
        top_due_customers = db.query(Customer).filter(
            Customer.store_id == store_id,
            Customer.outstanding_balance > 0,
            Customer.is_deleted == False
        ).order_by(desc(Customer.outstanding_balance)).limit(5).all()

        total_market_due = db.query(func.sum(Customer.outstanding_balance)).filter(
            Customer.store_id == store_id,
            Customer.is_deleted == False
        ).scalar() or 0.0

        total_due_count = db.query(func.count(Customer.id)).filter(
            Customer.store_id == store_id,
            Customer.outstanding_balance > 0,
            Customer.is_deleted == False
        ).scalar() or 0

        lines = []
        for idx, c in enumerate(top_due_customers, 1):
            full_name = f"{c.first_name} {c.last_name or ''}".strip()
            lines.append(f"{idx}. **{full_name}**: {_format_currency(float(c.outstanding_balance))} 📞 `{c.phone_number}`")

        msg = (
            f"👥 **Market Udhari & Customer Dues Report:**\n\n"
            f"- 💰 **Total Outstanding Dues:** **{_format_currency(float(total_market_due))}**\n"
            f"- 👤 **Customers with Pending Balance:** **{total_due_count}** grahak\n\n"
        )
        if lines:
            msg += "**Top 5 Pending Udhari Customers:**\n" + "\n".join(lines) + "\n\n*(Full list is available under Customers/CRM module)*"
        else:
            msg += "✅ **Great! Kisi bhi grahak ka paisa pending nahi hai.**"

        return {"response": msg, "source": "local"}

    # 5. Stock / Inventory
    stock_triggers = ["stock", "inventory", "maal", "kitna maal", "sona kitna", "chandi kitni", "gold stock", "silver stock", "items count"]
    if any(k in prompt for k in stock_triggers) and not re.search(r"\b(exchange|purana|purani|old|scrap|badli)\b", prompt):
        total_items = db.query(StockItem).filter(
            StockItem.store_id == store_id,
            StockItem.status.in_(["Available", "Active"])
        ).count()

        gold_items = db.query(StockItem).filter(
            StockItem.store_id == store_id,
            StockItem.status.in_(["Available", "Active"]),
            StockItem.metal.ilike("%gold%")
        ).all()
        gold_count = len(gold_items)
        gold_gross_wt = sum(float(i.gross_weight or 0) for i in gold_items)
        gold_net_wt = sum(float(i.net_weight or 0) for i in gold_items)

        silver_items = db.query(StockItem).filter(
            StockItem.store_id == store_id,
            StockItem.status.in_(["Available", "Active"]),
            StockItem.metal.ilike("%silver%")
        ).all()
        silver_count = len(silver_items)
        silver_gross_wt = sum(float(i.gross_weight or 0) for i in silver_items)
        silver_net_wt = sum(float(i.net_weight or 0) for i in silver_items)

        categories = db.query(StockItem.category, func.count(StockItem.id)).filter(
            StockItem.store_id == store_id,
            StockItem.status.in_(["Available", "Active"])
        ).group_by(StockItem.category).order_by(desc(func.count(StockItem.id))).limit(5).all()

        cat_lines = [f"- **{cat or 'General'}**: {cnt} items" for cat, cnt in categories]

        msg = (
            f"⚖️ **Store Inventory & Stock Summary:**\n\n"
            f"- 📦 **Total Ready Items:** **{total_items}** items in stock\n\n"
            f"🟡 **Gold Stock:**\n"
            f"- Count: **{gold_count}** items\n"
            f"- Gross Weight: **{gold_gross_wt:,.3f}g**\n"
            f"- Net Weight: **{gold_net_wt:,.3f}g**\n\n"
            f"⚪ **Silver Stock:**\n"
            f"- Count: **{silver_count}** items\n"
            f"- Gross Weight: **{silver_gross_wt:,.3f}g**\n"
            f"- Net Weight: **{silver_net_wt:,.3f}g**\n\n"
        )
        if cat_lines:
            msg += "**Top Categories in Stock:**\n" + "\n".join(cat_lines)

        return {"response": msg, "source": "local"}

    # 6. Expenses
    expense_triggers = ["kharcha", "kharch", "expense", "expenses", "overhead"]
    if any(k in prompt for k in expense_triggers):
        is_month = "month" in prompt or "mahina" in prompt or "mahine" in prompt
        if is_month:
            exp_sum = db.query(func.sum(Expense.amount)).filter(
                Expense.store_id == store_id,
                Expense.expense_date >= start_month.date()
            ).scalar() or 0.0
            period_name = "Is Mahine Ka Kharcha (This Month)"
        else:
            exp_sum = db.query(func.sum(Expense.amount)).filter(
                Expense.store_id == store_id,
                Expense.expense_date >= start_today.date()
            ).scalar() or 0.0
            period_name = "Aaj Ka Kharcha (Today)"

        recent_expenses = db.query(Expense).filter(
            Expense.store_id == store_id
        ).order_by(desc(Expense.expense_date)).limit(4).all()

        exp_lines = [f"- {e.description or e.category}: {_format_currency(float(e.amount))} ({e.expense_date})" for e in recent_expenses]

        msg = (
            f"💸 **Shop Expense Report:**\n\n"
            f"- 🧾 **{period_name}:** **{_format_currency(float(exp_sum))}**\n\n"
        )
        if exp_lines:
            msg += "**Recent Recorded Expenses:**\n" + "\n".join(exp_lines)

        return {"response": msg, "source": "local"}

    # 7. Suppliers
    supplier_triggers = ["supplier", "suppliers", "karigar", "wholesaler", "purchase", "khareed"]
    if any(k in prompt for k in supplier_triggers):
        total_supplier_due = db.query(func.sum(Supplier.outstanding_balance)).filter(
            Supplier.store_id == store_id,
            Supplier.is_deleted == False
        ).scalar() or 0.0

        top_suppliers = db.query(Supplier).filter(
            Supplier.store_id == store_id,
            Supplier.outstanding_balance > 0,
            Supplier.is_deleted == False
        ).order_by(desc(Supplier.outstanding_balance)).limit(5).all()

        today_purchases = db.query(func.sum(Purchase.grand_total)).filter(
            Purchase.store_id == store_id,
            Purchase.created_at >= start_today
        ).scalar() or 0.0

        lines = [f"- **{s.name}**: {_format_currency(float(s.outstanding_balance))} 📞 `{s.mobile}`" for s in top_suppliers]

        msg = (
            f"🏭 **Supplier & Karigar Dues Report:**\n\n"
            f"- 💰 **Total Payable to Suppliers:** **{_format_currency(float(total_supplier_due))}**\n"
            f"- 📦 **Today's New Purchases:** {_format_currency(float(today_purchases))}\n\n"
        )
        if lines:
            msg += "**Top Pending Supplier Balances:**\n" + "\n".join(lines)
        else:
            msg += "✅ Kisi supplier ka pending balance record nahi hai."

        return {"response": msg, "source": "local"}

    # 8. Exchange
    exchange_triggers = ["exchange", "old gold", "purana sona", "badli", "scrap", "purani chandi"]
    if any(k in prompt for k in exchange_triggers):
        today_exchanges = db.query(Exchange).filter(
            Exchange.store_id == store_id,
            Exchange.exchange_date >= start_today
        ).all()

        count = len(today_exchanges)
        total_old_val = sum(float(e.total_old_value or 0) for e in today_exchanges)
        gold_wt = sum(float(e.gold_balance_metal_weight or 0) for e in today_exchanges)
        silver_wt = sum(float(e.silver_balance_metal_weight or 0) for e in today_exchanges)

        return {
            "response": (
                f"🔄 **Today's Exchange & Old Metal Summary:**\n\n"
                f"- 🧾 **Total Exchanges Today:** **{count}** transactions\n"
                f"- 💰 **Total Old Metal Value:** {_format_currency(total_old_val)}\n"
                f"- 🟡 **Old Gold Metal Weight:** **{gold_wt:,.3f}g**\n"
                f"- ⚪ **Old Silver Metal Weight:** **{silver_wt:,.3f}g**\n\n"
                f"*(Detailed logs available under Exchange module)*"
            ),
            "source": "local"
        }

    # 9. Customer Search
    if "customer" in prompt or "grahak" in prompt or "phone" in prompt or re.search(r"\b\d{10}\b", prompt):
        phone_match = re.search(r"\b\d{10}\b", prompt)
        clean_search = prompt.replace("search", "").replace("customer", "").replace("grahak", "").replace("phone", "").strip()

        customer_query = db.query(Customer).filter(
            Customer.store_id == store_id,
            Customer.is_deleted == False
        )
        if phone_match:
            target_phone = phone_match.group(0)
            c = customer_query.filter(Customer.phone_number.contains(target_phone)).first()
        elif clean_search:
            c = customer_query.filter(
                or_(
                    Customer.first_name.ilike(f"%{clean_search}%"),
                    Customer.last_name.ilike(f"%{clean_search}%"),
                    Customer.phone_number.contains(clean_search)
                )
            ).first()
        else:
            c = None

        if c:
            full_name = f"{c.first_name} {c.last_name or ''}".strip()
            total_invoices = db.query(func.count(Invoice.id)).filter(
                Invoice.store_id == store_id,
                Invoice.customer_id == c.id
            ).scalar() or 0

            return {
                "response": (
                    f"👤 **Customer Profile Found:**\n\n"
                    f"- **Name:** **{full_name}**\n"
                    f"- 📞 **Phone:** `{c.phone_number}`\n"
                    f"- 📍 **Address:** {c.city or 'N/A'}, {c.state or ''}\n"
                    f"- 💰 **Pending Udhari:** **{_format_currency(float(c.outstanding_balance or 0))}**\n"
                    f"- 🪙 **Fine Gold Due:** {float(c.fine_gold_balance or 0):,.3f}g\n"
                    f"- 🧾 **Total Orders:** {total_invoices} bills created\n"
                ),
                "source": "local"
            }
        elif clean_search:
            return {
                "response": f"🔍 '{clean_search}' naam ya number ka koi grahak nahi mila. Kripya sahi naam ya 10-digit number check karein.",
                "source": "local"
            }

    # 10. Specific Invoice Search
    inv_match = re.search(r"(?:inv-?|bill-?|#)\s*([0-9a-zA-Z-]+)", prompt)
    if inv_match or (("bill" in prompt or "invoice" in prompt) and any(c.isdigit() for c in prompt)):
        search_term = inv_match.group(1) if inv_match else "".join(c for c in prompt if c.isalnum() or c == '-')
        inv = db.query(Invoice).filter(
            Invoice.store_id == store_id,
            or_(
                Invoice.invoice_number.ilike(f"%{search_term}%"),
                func.cast(Invoice.id, String(50)) == search_term
            )
        ).first()

        if inv:
            cust_name = "Walk-in Customer"
            if inv.customer_id:
                cust = db.query(Customer).filter_by(id=inv.customer_id).first()
                if cust:
                    cust_name = f"{cust.first_name} {cust.last_name or ''}".strip()

            date_str = inv.invoice_date.strftime("%d %b %Y, %I:%M %p") if inv.invoice_date else "N/A"
            return {
                "response": (
                    f"🧾 **Invoice Details Found:**\n\n"
                    f"- **Invoice Number:** `{inv.invoice_number}`\n"
                    f"- 👤 **Customer:** {cust_name}\n"
                    f"- 📅 **Date:** {date_str}\n"
                    f"- 💰 **Grand Total:** **{_format_currency(float(inv.grand_total))}**\n"
                    f"- 💵 **Paid Amount:** {_format_currency(float(inv.cash_received or 0))}\n"
                    f"- ⏳ **Balance Amount:** {_format_currency(float(inv.balance_amount or 0))}\n"
                    f"- 🏷️ **Status:** {inv.status.value if hasattr(inv.status, 'value') else (inv.status or 'Completed')}"
                ),
                "source": "local"
            }

    # 11. Quick Calculator
    calc_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:g|gram|gms)?\s*(?:of)?\s*(24k|22k|18k|gold|silver)?", prompt)
    rate_match = re.search(r"(?:rate|bhav|at|@)\s*(\d{4,6})", prompt)
    if calc_match and rate_match:
        weight = float(calc_match.group(1))
        rate_val = float(rate_match.group(1))
        rate_per_g = rate_val if rate_val < 15000 else (rate_val / 10.0)
        metal_cost = weight * rate_per_g
        gst = metal_cost * 0.03
        total_est = metal_cost + gst
        return {
            "response": (
                f"🧮 **Instant Jewellery Price Estimation:**\n\n"
                f"- **Weight:** {weight} grams\n"
                f"- **Rate:** ₹{rate_per_g:,.2f}/g (₹{rate_per_g*10:,.2f} per 10g)\n"
                f"- **Base Metal Cost:** {_format_currency(metal_cost)}\n"
                f"- **GST (3%):** {_format_currency(gst)}\n"
                f"- ⭐ **Total Estimated Price (excl. making):** **{_format_currency(total_est)}**"
            ),
            "source": "local"
        }

    # 12. Fallback
    return {
        "response": (
            "🤖 **Main aapki baat samajh nahi paya.** Kripya ye pooch kar dekhein:\n\n"
            "- 📊 *Aaj ki sale kitni hui?*\n"
            "- 👥 *Kiske paise baaki hain? (Top udhari)*\n"
            "- ⚖️ *Gold aur silver stock kitna hai?*\n"
            "- 💰 *Aaj ka gold rate kya hai?*\n"
            "- 💸 *Aaj ka kharcha kitna hua?*\n"
            "- 🔍 *Customer search [naam ya phone number]*"
        ),
        "source": "local"
    }


class GeminiKeyConfig(BaseModel):
    api_key: str


@router.get("/status")
def get_ai_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    key = get_effective_gemini_key(db)
    is_active = bool(key and not key.startswith("your-gemini"))
    masked = (key[:6] + "..." + key[-4:]) if (key and len(key) > 10) else ("Configured" if key else "")
    return {
        "status": "online",
        "gemini_active": is_active,
        "model": settings.GEMINI_MODEL or "gemini-2.5-flash",
        "mode": "gemini_online" if is_active else "local_offline_rule_engine",
        "masked_key": masked
    }


@router.post("/configure-key")
def configure_gemini_key(
    payload: GeminiKeyConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    key_val = payload.api_key.strip()
    try:
        from app.models.system_setting import SystemSetting
        existing = db.query(SystemSetting).filter(SystemSetting.setting_key == "GEMINI_API_KEY").first()
        if existing:
            existing.setting_value = key_val
        else:
            new_s = SystemSetting(setting_key="GEMINI_API_KEY", setting_value=key_val, description="Google Gemini API Key for AI Assistant")
            db.add(new_s)
        db.commit()
    except Exception as e:
        logger.warning(f"Could not persist GEMINI_API_KEY to DB: {e}")
        db.rollback()

    try:
        from app.core.config import DATA_ENV, DATA_DIR
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        env_lines = []
        if DATA_ENV.exists():
            with open(DATA_ENV, "r", encoding="utf-8") as f:
                env_lines = [l for l in f.readlines() if not l.strip().startswith("GEMINI_API_KEY=")]
        env_lines.append(f"GEMINI_API_KEY={key_val}\n")
        with open(DATA_ENV, "w", encoding="utf-8") as f:
            f.writelines(env_lines)
    except Exception as e:
        logger.warning(f"Could not write to DATA_ENV: {e}")

    settings.GEMINI_API_KEY = key_val
    return {"status": "success", "gemini_active": bool(key_val), "message": "Gemini API Key saved successfully!"}


@router.post("/chat")
def process_ai_chat(
    query: AIQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Hybrid Generative AI Assistant:
    1. If GEMINI_API_KEY is configured, calls Google Gemini API with real-time,
       tenant-isolated ERP metrics for natural, fluid bilingual conversations.
    2. Otherwise, seamlessly falls back to high-speed deterministic local rules.
    """
    store_id = require_tenant_id(current_user)
    raw_prompt = query.prompt.strip()
    prompt = raw_prompt.lower()

    # Step 1: Attempt Gemini LLM generation if API Key is available
    effective_key = get_effective_gemini_key(db)
    if effective_key:
        store_context = _build_store_context(db, store_id, prompt)
        history_dicts = [{"role": h.role, "text": h.text} for h in (query.history or [])]
        gemini_response = call_gemini_api(
            prompt=raw_prompt,
            context=store_context,
            history=history_dicts,
            api_key=effective_key
        )
        if gemini_response:
            return {
                "response": gemini_response,
                "source": "gemini",
                "model": settings.GEMINI_MODEL or "gemini-2.5-flash"
            }

    # Step 2: High-speed local fallback engine
    return _local_rule_fallback(prompt, store_id, db)

