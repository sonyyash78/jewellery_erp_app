from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.metal_type import MetalType
from app.models.purity import Purity
from app.models.gold_rate import GoldRate
from app.models.silver_rate import SilverRate
from app.schemas.metal_rate import RateCreate
from fastapi import HTTPException

def seed_default_metals(db: Session):
    gold = db.query(MetalType).filter(MetalType.name == "Gold").first()
    if not gold:
        gold = MetalType(name="Gold")
        db.add(gold)
        db.commit()
        db.refresh(gold)
        purities = [
            Purity(metal_type_id=gold.id, karat_name="24K", percentage=99.9),
            Purity(metal_type_id=gold.id, karat_name="22K", percentage=91.6),
            Purity(metal_type_id=gold.id, karat_name="20K", percentage=83.3),
            Purity(metal_type_id=gold.id, karat_name="18K", percentage=75.0),
        ]
        db.add_all(purities)

    silver = db.query(MetalType).filter(MetalType.name == "Silver").first()
    if not silver:
        silver = MetalType(name="Silver")
        db.add(silver)
        db.commit()
        db.refresh(silver)
        purities = [
            Purity(metal_type_id=silver.id, karat_name="999", percentage=99.9),
            Purity(metal_type_id=silver.id, karat_name="925", percentage=92.5),
            Purity(metal_type_id=silver.id, karat_name="Custom", percentage=100.0),
        ]
        db.add_all(purities)
    db.commit()
    return {"message": "Defaults seeded"}

def add_rate(db: Session, rate_in: RateCreate):
    purity = db.query(Purity).filter(Purity.id == rate_in.purity_id).first()
    if not purity:
        raise HTTPException(status_code=404, detail="Purity not found")
        
    if rate_in.metal_type.lower() == "gold":
        new_rate = GoldRate(purity_id=rate_in.purity_id, rate_per_gram=rate_in.rate_per_gram)
        db.add(new_rate)
    elif rate_in.metal_type.lower() == "silver":
        new_rate = SilverRate(purity_id=rate_in.purity_id, rate_per_gram=rate_in.rate_per_gram)
        db.add(new_rate)
    else:
        raise HTTPException(status_code=400, detail="metal_type must be Gold or Silver")
    
    db.commit()
    db.refresh(new_rate)
    return new_rate

def get_latest_rates(db: Session):
    gold_purities = db.query(Purity).join(MetalType).filter(MetalType.name == "Gold").all()
    silver_purities = db.query(Purity).join(MetalType).filter(MetalType.name == "Silver").all()
    
    latest_rates = []
    
    for p in gold_purities:
        rate = db.query(GoldRate).filter(GoldRate.purity_id == p.id).order_by(desc(GoldRate.effective_datetime)).first()
        if rate:
            rate.purity = p
            latest_rates.append(rate)
            
    for p in silver_purities:
        rate = db.query(SilverRate).filter(SilverRate.purity_id == p.id).order_by(desc(SilverRate.effective_datetime)).first()
        if rate:
            rate.purity = p
            latest_rates.append(rate)
            
    return latest_rates

def get_rate_history(db: Session, purity_id: int):
    purity = db.query(Purity).join(MetalType).filter(Purity.id == purity_id).first()
    if not purity:
        raise HTTPException(status_code=404, detail="Purity not found")
        
    if purity.metal_type.name == "Gold":
        history = db.query(GoldRate).filter(GoldRate.purity_id == purity_id).order_by(desc(GoldRate.effective_datetime)).all()
    else:
        history = db.query(SilverRate).filter(SilverRate.purity_id == purity_id).order_by(desc(SilverRate.effective_datetime)).all()
        
    return {"purity": purity, "history": history}
