#!/usr/bin/env python3
"""
Simple database initialization script
"""
import os
import sys
import time
import subprocess

def get_container_name(service_name):
    """Get the actual container name for a service"""
    try:
        result = subprocess.run([
            'docker-compose', 'ps', '-q', service_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            container_id = result.stdout.strip()
            # Get container name from ID
            name_result = subprocess.run([
                'docker', 'inspect', '--format', '{{.Name}}', container_id
            ], capture_output=True, text=True)
            
            if name_result.returncode == 0:
                return name_result.stdout.strip().lstrip('/')
    except Exception:
        pass
    
    # Fallback to default naming convention
    return f"meet-{service_name}-1"

def wait_for_postgres():
    """Wait for PostgreSQL to be ready"""
    max_retries = 30
    retry_count = 0
    
    postgres_container = get_container_name('postgres')
    print(f"🔍 Using PostgreSQL container: {postgres_container}")
    
    while retry_count < max_retries:
        try:
            # Test connection using psql
            result = subprocess.run([
                'docker', 'exec', postgres_container, 
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
        
        backend_container = get_container_name('backend')
        print(f"🔍 Using backend container: {backend_container}")
        
        # Run the database initialization inside the backend container
        result = subprocess.run([
            'docker', 'exec', backend_container,
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
