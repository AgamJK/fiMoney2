#!/usr/bin/env python3
"""
Initialize the database with required tables and initial data.
"""import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.core.config import settings
from app.db.session import engine, Base
from app.db.init_db import init_db
from app.initial_data import create_tables

def init() -> None:
    """Initialize the database."""
    print("Creating database tables...")
    create_tables()
    
    print("Initializing data...")
    init_db()
    
    print("Database initialization complete!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init()
