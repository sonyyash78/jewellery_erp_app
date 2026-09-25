from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel
from app.api.dependencies import get_db, get_current_user
from app.models.setting import Setting
from app.models.user import User
from app.schemas.metal_rate import MetalRateResponse
from app.services import metal_rate_service
import os
import shutil

router = APIRouter(dependencies=[Depends(get_current_user)])

class SettingItem(BaseModel):
    key: str
    value: str

from app.models.store import Store

@router.get("/")
def get_all_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store_id = current_user.tenant_id or 1
    settings = db.query(Setting).all()
    res = {s.key: s.value for s in settings}
    
    # Store-specific overrides for all custom fields
    if store_id != 1:
        prefix = f"store_{store_id}_"
        for s in settings:
            if s.key.startswith(prefix):
                pure_key = s.key[len(prefix):]
                res[pure_key] = s.value
                
    # Store model direct overrides
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        res["business_name"] = store.name
        res["store_name"] = store.name
        if store.phone:
            res["phone"] = store.phone
            res["store_phone"] = store.phone
        elif store_id != 1 and "phone" not in res:
            res["phone"] = ""
            res["store_phone"] = ""

        if store.email:
            res["email"] = store.email
            res["store_email"] = store.email
        elif store_id != 1 and "email" not in res:
            res["email"] = current_user.email or ""
            res["store_email"] = current_user.email or ""

        if store.address:
            res["address"] = store.address
            res["store_address"] = store.address
        elif store_id != 1 and "address" not in res:
            res["address"] = ""
            res["store_address"] = ""

        if store.gstin:
            res["gstin"] = store.gstin
            res["store_gstin"] = store.gstin
        elif store_id != 1 and "gstin" not in res:
            res["gstin"] = ""
            res["store_gstin"] = ""

        if store.logo_url:
            res["logo_url"] = store.logo_url
        else:
            res["logo_url"] = "/static/logo.png"

        if "upi_name" not in res or not res["upi_name"]:
            res["upi_name"] = store.name

    return res

@router.post("/")
def update_settings(
    settings_in: List[SettingItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import re
    store_id = current_user.tenant_id or 1
    store = db.query(Store).filter(Store.id == store_id).first()

    for item in settings_in:
        clean_key = item.key
        while clean_key.startswith("store_"):
            m = re.match(r"^store_\d+_(.*)$", clean_key)
            if m:
                clean_key = m.group(1)
            else:
                break

        # Don't overwrite an existing custom logo with default /static/logo.png
        if clean_key == "logo_url" and item.value == "/static/logo.png" and store and store.logo_url and store.logo_url != "/static/logo.png":
            continue

        # Update Store model directly
        if store:
            if clean_key in ("business_name", "store_name"):
                store.name = item.value
            elif clean_key in ("phone", "store_phone"):
                store.phone = item.value
            elif clean_key in ("email", "store_email"):
                store.email = item.value
            elif clean_key in ("address", "store_address"):
                store.address = item.value
            elif clean_key in ("gstin", "store_gstin"):
                store.gstin = item.value
            elif clean_key == "logo_url":
                store.logo_url = item.value

        # For store-specific settings when store_id != 1
        if store_id != 1:
            st_key = f"store_{store_id}_{clean_key}"
            s_obj = db.query(Setting).filter(Setting.key == st_key).first()
            if s_obj:
                s_obj.value = item.value
            else:
                db.add(Setting(key=st_key, value=item.value))
        else:
            # Update generic setting
            setting = db.query(Setting).filter(Setting.key == clean_key).first()
            if setting:
                setting.value = item.value
            else:
                db.add(Setting(key=clean_key, value=item.value))

    db.commit()
    if store:
        db.refresh(store)
    return {
        "message": "Settings updated",
        "store_name": store.name if store else "Jewellery ERP",
        "business_name": store.name if store else "Jewellery ERP",
        "logo_url": store.logo_url if store and store.logo_url else "/static/logo.png"
    }

@router.post("/logo")
async def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store_id = current_user.tenant_id or 1
    
    # Locate all static directories
    target_static_dirs = [
        os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "static")),
        os.path.abspath(r"C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\backend\static"),
        os.path.abspath(r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\static")
    ]
    # Deduplicate while preserving order
    seen = set()
    valid_dirs = []
    for d in target_static_dirs:
        if d not in seen:
            seen.add(d)
            try:
                os.makedirs(d, exist_ok=True)
                valid_dirs.append(d)
            except Exception:
                pass
                
    file_bytes = await file.read()
    
    # Determine extension
    ext = ".png"
    if file.filename:
        _, file_ext = os.path.splitext(file.filename.lower())
        if file_ext in ('.png', '.jpg', '.jpeg', '.webp'):
            ext = file_ext
            
    primary_filename = f"logo_store_{store_id}{ext}"
    
    # Write to target files across all static directories
    filenames_to_write = {
        primary_filename,
        f"logo_store_{store_id}.png",
        "logo.png"  # Always update global fallback so any unassigned or default views get latest logo
    }
    if store_id in (3, 5):
        filenames_to_write.add("logo_store_5.png")
        filenames_to_write.add("logo_store_3.png")
    filenames_to_write.add("logo_store_1.png")
    
    for s_dir in valid_dirs:
        for fname in filenames_to_write:
            try:
                dest = os.path.join(s_dir, fname)
                with open(dest, "wb") as buf:
                    buf.write(file_bytes)
            except Exception:
                pass
                
    logo_url = f"/static/{primary_filename}"
    
    # Update Store models
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        store.logo_url = logo_url
        
    store1 = db.query(Store).filter(Store.id == 1).first()
    if store1 and not store1.logo_url:
        store1.logo_url = logo_url

    # Persist setting keys
    st_key = f"store_{store_id}_logo_url"
    s_obj = db.query(Setting).filter(Setting.key == st_key).first()
    if s_obj:
        s_obj.value = logo_url
    else:
        db.add(Setting(key=st_key, value=logo_url))

    s_gen = db.query(Setting).filter(Setting.key == "logo_url").first()
    if s_gen:
        s_gen.value = logo_url
    else:
        db.add(Setting(key="logo_url", value=logo_url))
            
    db.commit()
    if store:
        db.refresh(store)

    return {"message": "Logo updated", "url": logo_url, "store_id": store_id}

@router.get("/metal-rates", response_model=List[MetalRateResponse])
def get_metal_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the currently active rates for all purities."""
    return metal_rate_service.get_latest_rates(db)
