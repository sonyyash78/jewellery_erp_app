from sqlalchemy import Integer, String, DECIMAL, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class PurchaseItem(Base):
    __tablename__ = 'purchase_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purchase_id: Mapped[int] = mapped_column(Integer, ForeignKey('purchases.id', ondelete='CASCADE'))
    
    metal_type: Mapped[str] = mapped_column(String(50)) # 'Gold' or 'Silver'
    item_name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Weight
    gross_weight: Mapped[float] = mapped_column(DECIMAL(10, 3))
    stone_weight: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    net_weight: Mapped[float] = mapped_column(DECIMAL(10, 3))
    
    # Purity / Math
    touch_purity: Mapped[float] = mapped_column(DECIMAL(5, 2))
    wastage: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0) # For silver
    fine_weight: Mapped[float] = mapped_column(DECIMAL(10, 3)) # Recovered pure metal
    
    # Financials
    metal_rate: Mapped[float] = mapped_column(DECIMAL(10, 2))
    metal_value: Mapped[float] = mapped_column(DECIMAL(12, 2))
    
    # Deductions
    labour_charge: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    testing_melting_charge: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    hallmark_charge: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    other_charges: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    discount: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    
    taxable_amount: Mapped[float] = mapped_column(DECIMAL(12, 2))
    
    purchase: Mapped['Purchase'] = relationship('Purchase', back_populates='items')
