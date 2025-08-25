from .core.config import Settings, get_settings

# Initialize settings
settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
