from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime, date
from app.models.accounting import PaymentMode, ExpenseCategory

class PaymentBase(BaseModel):
    bill_id: Optional[int] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    amount: Decimal
    payment_mode: PaymentMode
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    payment_date: datetime
    model_config = ConfigDict(from_attributes=True)

class ExpenseBase(BaseModel):
    category: ExpenseCategory
    amount: Decimal
    description: Optional[str] = None
    expense_date: date

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
