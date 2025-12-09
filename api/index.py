"""
Vercel serverless function entry point for FastAPI application.
"""

import os
import sys
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

# Set environment variables for Vercel
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("DEBUG", "false")

# Import and run FastAPI app
from main import app

# Vercel expects a handler function
handler = app