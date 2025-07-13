#!/usr/bin/env python3
"""
Railway Deployment Script
Runs the authenticated Streamlit dashboard for Railway hosting
"""
import os
import sys
import subprocess

def main():
    """Run the authenticated dashboard for Railway"""
    # Set default environment variables if not provided
    if not os.getenv("USER1_USERNAME"):
        os.environ["USER1_USERNAME"] = "admin"
    
    if not os.getenv("USER1_PASSWORD_HASH"):
        # Default hash for "admin123" - CHANGE THIS IN PRODUCTION
        os.environ["USER1_PASSWORD_HASH"] = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
    
    if not os.getenv("USER2_USERNAME"):
        os.environ["USER2_USERNAME"] = "viewer"
    
    if not os.getenv("USER2_PASSWORD_HASH"):
        # Default hash for "viewer123" - CHANGE THIS IN PRODUCTION  
        os.environ["USER2_PASSWORD_HASH"] = "fd5cb51bafd60950e5f1238503f2b8a8b1e4940c8f5b9cf4e24547e7c4e0c0ef"
    
    # Run Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "src/app/authenticated_dashboard.py",
        "--server.port", str(os.getenv("PORT", 8501)),
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    main()