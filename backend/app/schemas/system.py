from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

class NotificationBase(BaseModel):
    user_id: Optional[int] = None
    title: str
    message: str
    is_read: int = 0

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditLogBase(BaseModel):
    user_id: Optional[int] = None
    action: str
    entity: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[Any] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SettingsBase(BaseModel):
    key: str
    value: Any
    description: Optional[str] = None

class SettingsCreate(SettingsBase):
    pass

class SettingsUpdate(BaseModel):
    value: Any
    description: Optional[str] = None

class SettingsResponse(SettingsBase):
    id: int
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
