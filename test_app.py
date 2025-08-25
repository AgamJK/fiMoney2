import uvicorn
import asyncio
import sys
from pathlib import Path

async def test_app():
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=8082,
        log_level="info",
        reload=True
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    # Add the project root to the Python path
    project_root = str(Path(__file__).parent.absolute())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Run the test server
    asyncio.run(test_app())
