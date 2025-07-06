#!/usr/bin/env python3
"""
Setup script for Singapore News Intelligence Dashboard
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        sys.exit(1)
    print("✅ Python version check passed")

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "data/raw",
        "data/processed", 
        "logs",
        "config",
        "backend/api",
        "backend/models",
        "backend/utils",
        "backend/scrapers/sites",
        "test"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_gitkeep_files():
    """Create .gitkeep files to preserve empty directories."""
    gitkeep_dirs = [
        "data/raw",
        "data/processed",
        "logs"
    ]
    
    for directory in gitkeep_dirs:
        gitkeep_file = Path(directory) / ".gitkeep"
        gitkeep_file.touch(exist_ok=True)
        print(f"✅ Created .gitkeep in: {directory}")

def check_environment_file():
    """Check if .env file exists and provide instructions."""
    env_file = Path("config/.env")
    env_example = Path("config/env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  Environment file not found")
            print("📝 Please copy config/env.example to config/.env and configure your API keys")
            print("   cp config/env.example config/.env")
        else:
            print("❌ Environment template not found")
    else:
        print("✅ Environment file found")

def install_dependencies():
    """Install Python dependencies."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("Please run: pip install -r requirements.txt")

def check_google_credentials():
    """Check for Google Cloud credentials."""
    creds_file = Path("config/credentials.json")
    if not creds_file.exists():
        print("⚠️  Google Cloud credentials not found")
        print("📝 Please place your service account JSON file at config/credentials.json")
    else:
        print("✅ Google Cloud credentials found")

def create_log_file():
    """Create log file if it doesn't exist."""
    log_file = Path("logs/app.log")
    log_file.touch(exist_ok=True)
    print("✅ Log file created")

def main():
    """Main setup function."""
    print("🚀 Setting up Singapore News Intelligence Dashboard...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    print("\n📁 Creating project directories...")
    create_directories()
    create_gitkeep_files()
    
    # Check environment
    print("\n🔧 Checking environment configuration...")
    check_environment_file()
    check_google_credentials()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    install_dependencies()
    
    # Create log file
    print("\n📝 Setting up logging...")
    create_log_file()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure your API keys in config/.env")
    print("2. Add your Google Cloud credentials to config/credentials.json")
    print("3. Set up your Google Sheet ID in the environment file")
    print("4. Run the scraper: python backend/run_scraper.py")
    print("5. Start the API server: uvicorn backend.main:app --reload")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 