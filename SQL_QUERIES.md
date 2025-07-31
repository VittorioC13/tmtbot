# SQL Queries for User Management

## Database Connection
Your database is PostgreSQL hosted on Supabase. You can connect using:
- **Host**: aws-0-ap-southeast-1.pooler.supabase.com
- **Port**: 6543
- **Database**: postgres
- **Username**: postgres.raxegckgsveacgflvwbd
- **Password**: wdsjkdmmhaq

## Table Structure
The `user` table has the following structure:
```sql
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    is_paid BOOLEAN DEFAULT FALSE
);
```

## Useful SQL Queries

### 1. View All Users
```sql
SELECT id, username, is_paid FROM "user" ORDER BY id;
```

### 2. View Only Paid Users
```sql
SELECT id, username FROM "user" WHERE is_paid = TRUE ORDER BY id;
```

### 3. View Only Unpaid Users
```sql
SELECT id, username FROM "user" WHERE is_paid = FALSE ORDER BY id;
```

### 4. Count Users by Payment Status
```sql
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_paid = TRUE THEN 1 END) as paid_users,
    COUNT(CASE WHEN is_paid = FALSE THEN 1 END) as unpaid_users
FROM "user";
```

### 5. Update User Payment Status
```sql
-- Mark user as paid
UPDATE "user" SET is_paid = TRUE WHERE id = 1;

-- Mark user as unpaid
UPDATE "user" SET is_paid = FALSE WHERE id = 1;
```

### 6. Update User by Username
```sql
-- Mark user as paid by username
UPDATE "user" SET is_paid = TRUE WHERE username = 'john_doe';

-- Mark user as unpaid by username
UPDATE "user" SET is_paid = FALSE WHERE username = 'john_doe';
```

### 7. Search Users
```sql
-- Search by username (partial match)
SELECT id, username, is_paid FROM "user" 
WHERE username ILIKE '%john%' ORDER BY id;

-- Search by exact username
SELECT id, username, is_paid FROM "user" 
WHERE username = 'john_doe';
```

### 8. Delete User
```sql
-- Delete by ID
DELETE FROM "user" WHERE id = 1;

-- Delete by username
DELETE FROM "user" WHERE username = 'john_doe';
```

### 9. Create New User
```sql
-- Create unpaid user
INSERT INTO "user" (username, password, is_paid) 
VALUES ('new_user', 'password123', FALSE);

-- Create paid user
INSERT INTO "user" (username, password, is_paid) 
VALUES ('premium_user', 'password123', TRUE);
```

### 10. Get Payment Statistics
```sql
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_paid = TRUE THEN 1 END) as paid_users,
    COUNT(CASE WHEN is_paid = FALSE THEN 1 END) as unpaid_users,
    ROUND(
        (COUNT(CASE WHEN is_paid = TRUE THEN 1 END)::DECIMAL / COUNT(*)) * 100, 
        2
    ) as paid_percentage
FROM "user";
```

### 11. Find Recent Users
```sql
-- Users created in the last 7 days (approximate by ID)
SELECT id, username, is_paid FROM "user" 
WHERE id > (SELECT MAX(id) - 10 FROM "user") 
ORDER BY id DESC;
```

### 12. Bulk Operations
```sql
-- Mark all users as unpaid
UPDATE "user" SET is_paid = FALSE;

-- Mark all users as paid
UPDATE "user" SET is_paid = TRUE;

-- Delete all unpaid users
DELETE FROM "user" WHERE is_paid = FALSE;
```

## Using the Management Script

### Run the Interactive Tool
```bash
python api/manage_users.py
```

### Quick Commands
```bash
# List all users
python -c "
from api.manage_users import list_all_users
list_all_users()
"

# Get statistics
python -c "
from api.manage_users import get_payment_statistics
get_payment_statistics()
"

# Update user payment status
python -c "
from api.manage_users import update_user_payment_status
update_user_payment_status(1, True)  # Mark user ID 1 as paid
"
```

## Database Connection Tools

### Using psql (PostgreSQL CLI)
```bash
psql "postgresql://postgres.raxegckgsveacgflvwbd:wdsjkdmmhaq@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
```

### Using pgAdmin or DBeaver
- **Connection Type**: PostgreSQL
- **Host**: aws-0-ap-southeast-1.pooler.supabase.com
- **Port**: 6543
- **Database**: postgres
- **Username**: postgres.raxegckgsveacgflvwbd
- **Password**: wdsjkdmmhaq

## Common Tasks

### Check if a specific user exists
```sql
SELECT id, username, is_paid FROM "user" WHERE username = 'your_username';
```

### Find users who haven't paid
```sql
SELECT id, username FROM "user" WHERE is_paid = FALSE ORDER BY id;
```

### Get total revenue (assuming $10 per paid user)
```sql
SELECT 
    COUNT(CASE WHEN is_paid = TRUE THEN 1 END) * 10 as total_revenue
FROM "user";
```

### Export user data
```sql
-- Export all users to CSV format
SELECT 
    id,
    username,
    CASE WHEN is_paid THEN 'PAID' ELSE 'UNPAID' END as status
FROM "user" 
ORDER BY id;
```

## Security Notes

⚠️ **Important**: 
- Never share database credentials
- Use the management script for safer operations
- Always backup before bulk operations
- Test queries on a small dataset first 