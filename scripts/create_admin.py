#!/usr/bin/env python3
"""
Create a new admin user.
"""
import sys
import getpass
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.core.config import settings
from app.db.session import SessionLocal
from app import crud, schemas

def create_admin() -> None:
    """Create a new admin user."""
    db = SessionLocal()
    try:
        print("Create a new admin user")
        print("-" * 30)
        
        email = input("Email: ").strip()
        if not email:
            print("Email is required")
            return
            
        # Check if user already exists
        user = crud.user.get_by_email(db, email=email)
        if user:
            print(f"User with email {email} already exists")
            return
            
        full_name = input("Full name: ").strip()
        if not full_name:
            print("Full name is required")
            return
            
        while True:
            password = getpass.getpass("Password: ").strip()
            if not password:
                print("Password is required")
                continue
                
            confirm_password = getpass.getpass("Confirm password: ").strip()
            if password != confirm_password:
                print("Passwords do not match")
                continue
                
            break
            
        # Create user
        user_in = schemas.UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            is_superuser=True,
        )
        
        user = crud.user.create(db, obj_in=user_in)
        print(f"\nAdmin user {user.email} created successfully!")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
