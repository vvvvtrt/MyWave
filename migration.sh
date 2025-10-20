#!/bin/bash

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
OLD_CONTAINER="meet-postgres-1"
NEW_CONTAINER="meet-postgres-1"
DB_NAME="mywave"
DB_USER="mywave"
BACKUP_FILE="./mywave_backup_$(date +%Y%m%d_%H%M%S).sql"

echo "🔄 PostgreSQL Migration Script"
echo "================================"
echo ""

# Function to check if container exists
check_container() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${1}$"; then
        return 0
    else
        return 1
    fi
}

# Function to check if container is running
check_running() {
    if docker ps --format '{{.Names}}' | grep -q "^${1}$"; then
        return 0
    else
        return 1
    fi
}

# Function to wait for PostgreSQL
wait_for_postgres() {
    local container=$1
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for PostgreSQL to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec $container pg_isready -U $DB_USER -d $DB_NAME >/dev/null 2>&1; then
            echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ PostgreSQL failed to start${NC}"
    return 1
}

# Step 1: Check if old container exists
echo "1️⃣ Checking old container..."
if ! check_container "$OLD_CONTAINER"; then
    echo -e "${RED}❌ Old container '$OLD_CONTAINER' not found${NC}"
    exit 1
fi

if ! check_running "$OLD_CONTAINER"; then
    echo -e "${YELLOW}⚠️  Old container is not running. Starting it...${NC}"
    docker start $OLD_CONTAINER
    wait_for_postgres $OLD_CONTAINER
fi

echo -e "${GREEN}✅ Old container found and running${NC}"

# Step 2: Create backup
echo ""
echo "2️⃣ Creating backup from old container..."
echo "   Backup file: $BACKUP_FILE"

docker exec $OLD_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_FILE

if [ $? -eq 0 ] && [ -s $BACKUP_FILE ]; then
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo -e "${GREEN}✅ Backup created successfully (Size: $BACKUP_SIZE)${NC}"
else
    echo -e "${RED}❌ Backup failed${NC}"
    exit 1
fi

# Step 3: Stop old containers
echo ""
echo "3️⃣ Stopping old containers..."
docker-compose down
echo -e "${GREEN}✅ Containers stopped${NC}"

# Step 4: Optional - Remove old volume
echo ""
read -p "🗑️  Do you want to remove old volume? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   Removing old volume..."
    docker volume rm meet_postgres_data 2>/dev/null || true
    echo -e "${GREEN}✅ Old volume removed${NC}"
fi

# Step 5: Start new container
echo ""
echo "4️⃣ Starting new containers..."
docker-compose up -d postgres
wait_for_postgres $NEW_CONTAINER

# Step 6: Restore data
echo ""
echo "5️⃣ Restoring data to new container..."
docker exec -i $NEW_CONTAINER psql -U $DB_USER -d $DB_NAME < $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Data restored successfully${NC}"
else
    echo -e "${RED}❌ Data restoration failed${NC}"
    exit 1
fi

# Step 7: Verify data
echo ""
echo "6️⃣ Verifying data..."
TABLE_COUNT=$(docker exec $NEW_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo "   Tables found: $TABLE_COUNT"

if [ "$TABLE_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Data verification successful${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: No tables found${NC}"
fi

# Step 8: Start all services
echo ""
echo "7️⃣ Starting all services..."
docker-compose up -d
sleep 5

echo ""
echo "================================"
echo -e "${GREEN}🎉 Migration completed successfully!${NC}"
echo ""
echo "📋 Summary:"
echo "  - Backup file: $BACKUP_FILE"
echo "  - Tables migrated: $TABLE_COUNT"
echo ""
echo "💡 Next steps:"
echo "  1. Test your application"
echo "  2. If everything works, delete backup: rm $BACKUP_FILE"
echo "  3. View logs: docker-compose logs -f"
echo ""
echo "📊 Service status:"
docker-compose ps