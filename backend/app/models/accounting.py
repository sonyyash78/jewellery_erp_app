from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class PaymentMode(str, enum.Enum):
    CASH = "Cash"
    UPI = "UPI"
    BANK = "Bank"
    CARD = "Card"

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=True) # Can be related to a bill
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True) # Or just a general customer payment
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True) # Or supplier payment
    
    amount = Column(Numeric(12, 2), nullable=False)
    payment_mode = Column(Enum(PaymentMode), nullable=False)
    reference_number = Column(String(100)) # e.g. UTR number, Check number
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String(255))

    bill = relationship("Bill", back_populates="payments")

class ExpenseCategory(str, enum.Enum):
    SALARY = "Salary"
    RENT = "Rent"
    ELECTRICITY = "Electricity"
    MISC = "Misc"

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(Enum(ExpenseCategory), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(255))
    expense_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
