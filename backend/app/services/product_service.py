from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant
from app.models.product_variant_stone import ProductVariantStone
from app.models.audit_log import AuditLog
from app.schemas.product import ProductCreate
from fastapi import HTTPException

def log_action(db: Session, user_id: int, entity_name: str, entity_id: str, action: str):
    log = AuditLog(
        user_id=user_id,
        entity_name=entity_name,
        entity_id=entity_id,
        action=action,
        changes=None
    )
    db.add(log)

def get_products(db: Session, skip: int = 0, limit: int = 10, search: str = None):
    query = db.query(Product).filter(Product.is_deleted == False)
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku_prefix.ilike(f"%{search}%")
            )
        )
    total = query.count()
    items = query.order_by(desc(Product.id)).offset(skip).limit(limit).all()
    return total, items

def get_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id, Product.is_deleted == False).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

def create_product(db: Session, product_in: ProductCreate, user_id: int):
    db_product = Product(
        category_id=product_in.category_id,
        design_id=product_in.design_id,
        metal_type_id=product_in.metal_type_id,
        name=product_in.name,
        sku_prefix=product_in.sku_prefix,
        description=product_in.description
    )
    db.add(db_product)
    db.flush()

    for img in product_in.images:
        db_img = ProductImage(product_id=db_product.id, **img.model_dump())
        db.add(db_img)

    for var in product_in.variants:
        db_var = ProductVariant(
            product_id=db_product.id,
            purity_id=var.purity_id,
            standard_weight=var.standard_weight,
            size=var.size,
            making_charge_type=var.making_charge_type
        )
        db.add(db_var)
        db.flush()
        
        for st in var.stones:
            db_stone = ProductVariantStone(
                variant_id=db_var.id,
                **st.model_dump()
            )
            db.add(db_stone)
            
    db.commit()
    db.refresh(db_product)
    log_action(db, user_id, "Product", str(db_product.id), "CREATE")
    return db_product

def delete_product(db: Session, product_id: int, user_id: int):
    product = get_product(db, product_id)
    product.is_deleted = True
    db.commit()
    log_action(db, user_id, "Product", str(product.id), "DELETE")
