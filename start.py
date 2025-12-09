#!/usr/bin/env python3
"""
Startup script for the Gemini API wrapper server.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Check for .env file
env_file = current_dir / ".env"
if not env_file.exists():
    print("⚠️  Warning: .env file not found!")
    print("   Please copy .env.example to .env and configure your settings.")
    print("   Example: cp .env.example .env")
    print()

# Import and run the server
if __name__ == "__main__":
    import uvicorn
    from config.settings import settings

    print(f"🚀 Starting {settings.api_title} v{settings.api_version}")
    print(f"📍 Server will be available at: http://{settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🔍 Health Check: http://{settings.host}:{settings.port}/health")
    print()

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        app_dir=str(src_dir),
    )