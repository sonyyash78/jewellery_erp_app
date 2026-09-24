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

@router.get("/")
def get_all_settings(db: Session = Depends(get_db)):
    settings = db.query(Setting).all()
    return {s.key: s.value for s in settings}

@router.post("/")
def update_settings(settings_in: List[SettingItem], db: Session = Depends(get_db)):
    for item in settings_in:
        setting = db.query(Setting).filter(Setting.key == item.key).first()
        if setting:
            setting.value = item.value
        else:
            db.add(Setting(key=item.key, value=item.value))
    db.commit()
    return {"message": "Settings updated"}

@router.post("/logo")
async def upload_logo(file: UploadFile = File(...)):
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "static")
    os.makedirs(static_dir, exist_ok=True)
    
    file_location = os.path.join(static_dir, "logo.png")
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"message": "Logo updated", "url": "/static/logo.png"}

@router.get("/metal-rates", response_model=List[MetalRateResponse])
def get_metal_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the currently active rates for all purities."""
    return metal_rate_service.get_latest_rates(db)
