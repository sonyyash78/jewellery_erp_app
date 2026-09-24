from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from app.models.customer import Customer
from app.models.audit_log import AuditLog
from app.schemas.customer import CustomerCreate, CustomerUpdate
from fastapi import HTTPException
import json

def log_action(db: Session, user_id: int, entity_name: str, entity_id: str, action: str, changes: dict = None):
    log = AuditLog(
        user_id=user_id,
        entity_name=entity_name,
        entity_id=entity_id,
        action=action,
        changes=changes
    )
    db.add(log)

def get_customers(db: Session, skip: int = 0, limit: int = 10, search: str = None):
    query = db.query(Customer).filter(Customer.is_deleted == False)
    if search:
        query = query.filter(
            or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.phone_number.ilike(f"%{search}%")
            )
        )
    total = query.count()
    items = query.order_by(desc(Customer.created_at)).offset(skip).limit(limit).all()
    return total, items

def get_customer(db: Session, customer_id: int):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

def create_customer(db: Session, customer_in: CustomerCreate, user_id: int):
    db_customer = Customer(**customer_in.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    log_action(db, user_id, "Customer", str(db_customer.id), "CREATE", customer_in.model_dump())
    db.commit()
    return db_customer

def update_customer(db: Session, customer_id: int, customer_in: CustomerUpdate, user_id: int):
    db_customer = get_customer(db, customer_id)
    update_data = customer_in.model_dump(exclude_unset=True)
    
    if not update_data:
        return db_customer

    for field, value in update_data.items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)
    
    log_action(db, user_id, "Customer", str(db_customer.id), "UPDATE", update_data)
    db.commit()
    return db_customer

def delete_customer(db: Session, customer_id: int, user_id: int):
    db_customer = get_customer(db, customer_id)
    db_customer.is_deleted = True
    db.commit()
    
    log_action(db, user_id, "Customer", str(db_customer.id), "DELETE", {"is_deleted": True})
    db.commit()
    return db_customer
