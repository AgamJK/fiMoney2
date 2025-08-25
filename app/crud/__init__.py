from .base import CRUDBase
from .user import user as user_crud
from .user_settings import user_settings as user_settings_crud

# Export CRUD modules
user = user_crud
user_settings = user_settings_crud

__all__ = [
    "CRUDBase",
    "user",
    "user_settings",
]
