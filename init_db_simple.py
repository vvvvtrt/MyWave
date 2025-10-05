#!/usr/bin/env python3
"""
Simple database initialization script
"""
import os
import sys
import time
import subprocess

def wait_for_postgres():
    """Wait for PostgreSQL to be ready"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Test connection using psql
            result = subprocess.run([
                'docker', 'exec', 'meet-postgres-1', 
                'psql', '-U', 'mywave', '-d', 'mywave', '-c', 'SELECT 1;'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PostgreSQL is ready!")
                return True
        except Exception as e:
            pass
        
        retry_count += 1
        print(f"⏳ Waiting for PostgreSQL... ({retry_count}/{max_retries})")
        time.sleep(2)
    
    print("❌ Failed to connect to PostgreSQL after 60 seconds")
    return False

def create_tables():
    """Create database tables using docker exec"""
    try:
        print("🔨 Creating database tables...")
        
        # Run the database initialization inside the backend container
        result = subprocess.run([
            'docker', 'exec', 'meet-backend-1',
            'python', '-c', '''
import sys
sys.path.append("/app")
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
'''
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database tables created successfully!")
            return True
        else:
            print(f"❌ Error creating tables: {result.stderr}")
            return False
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
