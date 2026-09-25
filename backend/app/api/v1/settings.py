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
    
    # Store-specific overrides
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        res["business_name"] = store.name
        res["store_name"] = store.name
        if store.phone:
            res["phone"] = store.phone
            res["store_phone"] = store.phone
        elif store_id != 1:
            res["phone"] = ""
            res["store_phone"] = ""

        if store.email:
            res["email"] = store.email
            res["store_email"] = store.email
        elif store_id != 1:
            res["email"] = current_user.email or ""
            res["store_email"] = current_user.email or ""

        if store.address:
            res["address"] = store.address
            res["store_address"] = store.address
        elif store_id != 1:
            res["address"] = ""
            res["store_address"] = ""

        if store.gstin:
            res["gstin"] = store.gstin
            res["store_gstin"] = store.gstin
        elif store_id != 1:
            res["gstin"] = ""
            res["store_gstin"] = ""

        if store.logo_url:
            res["logo_url"] = store.logo_url
        else:
            res["logo_url"] = "/static/logo.png"

        res["upi_name"] = store.name
        if store_id != 1:
            store_upi = db.query(Setting).filter(Setting.key == f"store_{store_id}_upi_id").first()
            res["upi_id"] = store_upi.value if store_upi else ""

    return res

@router.post("/")
def update_settings(
    settings_in: List[SettingItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store_id = current_user.tenant_id or 1
    store = db.query(Store).filter(Store.id == store_id).first()

    for item in settings_in:
        # Update Store model directly
        if store:
            if item.key in ("business_name", "store_name"):
                store.name = item.value
            elif item.key in ("phone", "store_phone"):
                store.phone = item.value
            elif item.key in ("email", "store_email"):
                store.email = item.value
            elif item.key in ("address", "store_address"):
                store.address = item.value
            elif item.key in ("gstin", "store_gstin"):
                store.gstin = item.value
            elif item.key == "logo_url":
                store.logo_url = item.value

        # For store-specific UPI or settings, key by store_{store_id}_{key} if not root store
        if item.key == "upi_id" and store_id != 1:
            st_key = f"store_{store_id}_upi_id"
            s_obj = db.query(Setting).filter(Setting.key == st_key).first()
            if s_obj:
                s_obj.value = item.value
            else:
                db.add(Setting(key=st_key, value=item.value))
        else:
            # Update generic setting
            setting = db.query(Setting).filter(Setting.key == item.key).first()
            if setting:
                setting.value = item.value
            else:
                db.add(Setting(key=item.key, value=item.value))

    db.commit()
    return {"message": "Settings updated"}

@router.post("/logo")
async def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store_id = current_user.tenant_id or 1
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "static")
    os.makedirs(static_dir, exist_ok=True)
    
    filename = f"logo_store_{store_id}.png"
    file_location = os.path.join(static_dir, filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    logo_url = f"/static/{filename}"
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        store.logo_url = logo_url
        db.commit()

    return {"message": "Logo updated", "url": logo_url}

@router.get("/metal-rates", response_model=List[MetalRateResponse])
def get_metal_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the currently active rates for all purities."""
    return metal_rate_service.get_latest_rates(db)
