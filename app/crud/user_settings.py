from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import UserSettings
from app.schemas.user_settings import UserSettingsCreate, UserSettingsUpdate

class CRUDUserSettings(CRUDBase[UserSettings, UserSettingsCreate, UserSettingsUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: str) -> Optional[UserSettings]:
        return db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    def create_with_user(
        self, db: Session, *, obj_in: UserSettingsCreate, user_id: str
    ) -> UserSettings:
        db_obj = UserSettings(
            user_id=user_id,
            currency=obj_in.currency,
            timezone=obj_in.timezone,
            notification_preferences=obj_in.notification_preferences,
            dashboard_preferences=obj_in.dashboard_preferences,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_settings = CRUDUserSettings(UserSettings)
