import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from alembic import command
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from app import settings
from app.core.database import Base
from app.models import *  # noqa: F403, F401
from app.models.collaboration import Group, GroupExpense

def init_db():
    """Initialize the database by creating all tables"""
    # Create database if it doesn't exist
    engine = create_engine(settings.DATABASE_URL)
    if not database_exists(engine.url):
        create_database(engine.url)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Run migrations
    run_migrations()
    
    print("✅ Database initialized successfully!")

def run_migrations():
    """Run database migrations using Alembic"""
    # Get the directory containing this file
    current_dir = Path(__file__).parent.parent.parent
    
    # Set up Alembic config
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(current_dir / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
    
    # Run migrations
    command.upgrade(alembic_cfg, "head")
    print("✅ Database migrations applied successfully!")

def create_migration(message: str):
    """Create a new migration"""
    # Get the directory containing this file
    current_dir = Path(__file__).parent.parent.parent
    
    # Set up Alembic config
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(current_dir / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
    
    # Generate migration
    command.revision(
        alembic_cfg,
        autogenerate=True,
        message=message,
        autogenerate_args={
            'tables': None,  # All tables
        },
    )
    print("✅ Migration created successfully!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.core.db_init [init|migrate|create_migration] [message]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        init_db()
    elif command == "migrate":
        run_migrations()
    elif command == "create_migration":
        message = sys.argv[2] if len(sys.argv) > 2 else "auto-generated migration"
        create_migration(message)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
