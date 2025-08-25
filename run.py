#!/usr/bin/env python3
"""
Run the FastAPI application with uvicorn.
"""
import uvicorn
from pathlib import Path
import os

def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port: int, max_attempts: int = 10) -> int:
    port = start_port
    attempts = 0
    while attempts < max_attempts:
        if not is_port_in_use(port):
            return port
        port += 1
        attempts += 1
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

def main():
    """Run the FastAPI application."""
    # Load environment variables from .env file if it exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"Loading environment variables from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    default_port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENV", "development") == "development"
    
    # Find an available port
    port = find_available_port(default_port)
    if port != default_port:
        print(f"Port {default_port} is in use, using port {port} instead")
    
    print(f"Starting server on http://{host}:{port}")
    print(f"Environment: {'development' if reload else 'production'}")
    print(f"Docs: http://{host}:{port}/docs")
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=int(os.getenv("WORKERS", "1")),
    )

if __name__ == "__main__":
    main()
