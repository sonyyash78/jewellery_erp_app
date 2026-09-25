from sqlalchemy.orm import Session
from app.models.user import User
from app.models.store import Store

def ensure_user_store(db: Session, user: User) -> User:
    """
    Ensures that the given user has a valid isolated tenant store.
    - User ID 1 / admin username / admin email owns Store 1 ('Saideep Jewellers').
    - Every other user is strictly isolated to their own dedicated store.
    """
    if not user:
        return user

    is_root_admin = (
        user.id == 1 or 
        (user.username and user.username.lower() == "admin") or 
        (user.email and user.email.lower() in ("admin@example.com", "admin@saideep.com"))
    )

    if is_root_admin:
        store1 = db.query(Store).filter(Store.id == 1).first()
        if store1 and store1.owner_id != user.id:
            store1.owner_id = user.id
            db.commit()
        if user.tenant_id != 1:
            user.tenant_id = 1
            db.commit()
            db.refresh(user)
        return user

    # For all non-root users: they should never be mapped to Store 1!
    # 1. Check if user already owns a store
    user_store = db.query(Store).filter(Store.owner_id == user.id).first()
    if user_store:
        if user.tenant_id != user_store.id:
            user.tenant_id = user_store.id
            db.commit()
            db.refresh(user)
        return user

    # 2. Check if user has an assigned tenant_id other than 1
    if user.tenant_id and user.tenant_id != 1:
        valid_store = db.query(Store).filter(Store.id == user.tenant_id).first()
        if valid_store:
            return user

    # 3. Create a brand-new dedicated store for this user
    name_seed = user.full_name or (user.email.split('@')[0] if user.email else user.username)
    clean_name = name_seed.replace("Jewellers", "").replace("jewellers", "").strip().title()
    store_name = f"{clean_name or 'My'} Jewellers"

    new_store = Store(
        name=store_name,
        owner_id=user.id,
        email=user.email,
        is_active=True
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)

    user.tenant_id = new_store.id
    db.commit()
    db.refresh(user)
    return user
