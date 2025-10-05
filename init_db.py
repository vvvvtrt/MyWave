#!/usr/bin/env python3
"""
Database initialization script for PostgreSQL
"""
import os
import sys
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import Base, engine
from backend.app.config import settings

def wait_for_postgres():
    """Wait for PostgreSQL to be ready"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Test connection
            test_engine = create_engine(settings.DATABASE_URL)
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL is ready!")
            return True
        except OperationalError as e:
            retry_count += 1
            print(f"⏳ Waiting for PostgreSQL... ({retry_count}/{max_retries})")
            time.sleep(2)
    
    print("❌ Failed to connect to PostgreSQL after 60 seconds")
    return False

def create_tables():
    """Create all database tables"""
    try:
        print("🔨 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def main():
    print("🚀 Initializing database...")
    
    # Wait for PostgreSQL
    if not wait_for_postgres():
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        sys.exit(1)
    
    print("🎉 Database initialization completed!")

if __name__ == "__main__":
    main()
