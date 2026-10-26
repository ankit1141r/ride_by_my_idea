"""
Vercel Serverless Function Entry Point for RideConnect India.
Routes incoming serverless HTTP requests to the FastAPI application.
"""
import sys
import os

# Add parent directory to sys.path so app modules import properly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.main import app

# Vercel automatically picks up 'app' as the ASGI application
