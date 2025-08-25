import logging
from typing import Any

from fastapi import FastAPI
from sqlalchemy.orm import Session

from app import crud, models, schemas, settings
from app.db.session import SessionLocal

def init_db(app: FastAPI) -> None:
    """Initialize the database with default data."""
    db = SessionLocal()
    try:
        # Create first superuser
        user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not user:
            user_in = schemas.UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name="Admin",
                is_superuser=True,
            )
            user = crud.user.create(db, obj_in=user_in)
            print(f"Created superuser {settings.FIRST_SUPERUSER_EMAIL}")
            
            # Create default settings for the superuser
            settings_in = schemas.UserSettingsCreate(
                currency="INR",
                timezone="Asia/Kolkata",
                notification_preferences={"email": True, "push": True, "sms": False},
                dashboard_preferences={"default_view": "overview"}
            )
            crud.user_settings.create_with_user(
                db=db,
                obj_in=settings_in,
                user_id=user.id
            )
            print(f"Created default settings for {settings.FIRST_SUPERUSER_EMAIL}")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()

def create_tables() -> None:
    """
    Create all database tables.
    """
    from app.db.base_class import Base
    from app.db.session import engine
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
