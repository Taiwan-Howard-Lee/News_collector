#!/usr/bin/env python3
"""
Database setup script for Singapore News Intelligence Dashboard
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import sqlalchemy
        import psycopg2
        import alembic
        print("✅ All database dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def init_alembic():
    """Initialize Alembic if not already done."""
    if not Path("migrations").exists():
        print("📝 Initializing Alembic...")
        subprocess.run(["alembic", "init", "migrations"], check=True)
        print("✅ Alembic initialized")
    else:
        print("✅ Alembic already initialized")

def create_initial_migration():
    """Create initial migration for the database schema."""
    try:
        print("📝 Creating initial migration...")
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"], check=True)
        print("✅ Initial migration created")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Migration creation failed: {e}")
        print("This might be normal if the database is already set up")

def run_migrations():
    """Run database migrations."""
    try:
        print("🔄 Running database migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✅ Database migrations completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        return False
    return True

def test_database_connection():
    """Test database connection."""
    try:
        from backend.database.connection import check_db_connection
        if check_db_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def main():
    """Main database setup function."""
    print("🗄️  Setting up database for Singapore News Intelligence Dashboard...")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize Alembic
    init_alembic()
    
    # Create initial migration
    create_initial_migration()
    
    # Run migrations
    if not run_migrations():
        print("❌ Database setup failed")
        sys.exit(1)
    
    # Test connection
    if not test_database_connection():
        print("❌ Database connection test failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set up Railway PostgreSQL database")
    print("2. Update DATABASE_URL in your environment")
    print("3. Run migrations on Railway: alembic upgrade head")
    print("4. Start the application: uvicorn backend.main:app --reload")

if __name__ == "__main__":
    main() 