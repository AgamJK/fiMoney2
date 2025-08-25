#!/usr/bin/env python3
"""
Set up the database by creating tables and running migrations.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from alembic.config import Config
from alembic import command
from app.core.config import settings
from app.db.session import engine, Base
from app.initial_data import create_tables, init_db

def run_migrations() -> None:
    """Run database migrations."""
    print("Running database migrations...")
    
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up Alembic config
    alembic_cfg = Config(os.path.join(script_dir, "..", "alembic.ini"))
    
    # Set the database URL in the config
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
    
    # Run migrations
    command.upgrade(alembic_cfg, "head")
    print("Database migrations completed.")

def setup_database() -> None:
    """Set up the database by creating tables and initializing data."""
    print("Setting up database...")
    
    # Create tables
    create_tables()
    
    # Run migrations
    run_migrations()
    
    # Initialize data
    from fastapi import FastAPI
    app = FastAPI()
    init_db(app)
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
