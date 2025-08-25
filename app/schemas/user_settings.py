from typing import Dict, Optional
from pydantic import BaseModel

class UserSettingsBase(BaseModel):
    currency: str = "INR"
    timezone: str = "Asia/Kolkata"
    notification_preferences: Dict[str, bool] = {"email": True, "push": True, "sms": False}
    dashboard_preferences: Dict[str, str] = {"default_view": "overview"}

class UserSettingsCreate(UserSettingsBase):
    pass

class UserSettingsUpdate(UserSettingsBase):
    currency: Optional[str] = None
    timezone: Optional[str] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    dashboard_preferences: Optional[Dict[str, str]] = None

class UserSettingsInDBBase(UserSettingsBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True

class UserSettings(UserSettingsInDBBase):
    pass
