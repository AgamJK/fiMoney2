#!/usr/bin/env python3
"""
Generate a secure random secret key for the application.
"""
import secrets
import sys

def generate_secret_key() -> str:
    """Generate a secure random secret key."""
    return secrets.token_hex(32)

if __name__ == "__main__":
    print("SECRET_KEY=\"" + generate_secret_key() + "\"")
