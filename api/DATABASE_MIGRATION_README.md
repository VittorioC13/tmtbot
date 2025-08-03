# Database Migration: Adding sector_changed_at Column

This migration adds the `sector_changed_at` column to the User table to support the weekly sector change restriction feature for basic users.

## What this migration does:

- Adds a `sector_changed_at` TIMESTAMP column to the User table
- This column tracks when a basic user last changed their sector
- Enables the weekly sector change restriction feature.

## Migration Methods

### Method 1: Python Migration Script (Recommended)

1. **Navigate to the api directory:**
   ```bash
   cd api
   ```

2. **Run the migration script:**
   ```bash
   python migrate_add_sector_changed_at.py
   ```

3. **Check the output:**
   - ✅ Success: Column added successfully
   - ❌ Error: Check database connection

### Method 2: Direct SQL (Alternative)

1. **Connect to your PostgreSQL database:**
   ```bash
   psql -h your-host -U your-username -d your-database
   ```

2. **Run the SQL script:**
   ```sql
   \i add_sector_changed_at.sql
   ```

3. **Or run the SQL commands directly:**
   ```sql
   ALTER TABLE "user" ADD COLUMN sector_changed_at TIMESTAMP;
   ```

## Verification

After running the migration, you can verify it worked by:

1. **Checking the column exists:**
   ```sql
   SELECT column_name, data_type, is_nullable 
   FROM information_schema.columns 
   WHERE table_name = 'user' 
   AND column_name = 'sector_changed_at';
   ```

2. **Testing the feature:**
   - Login as a basic user
   - Try to change your sector
   - The system should now track when you change sectors

## Troubleshooting

### Common Issues:

1. **Database Connection Error:**
   - Check your database URL in `index.py`
   - Ensure your database is running
   - Verify your credentials

2. **Column Already Exists:**
   - This is normal if you've run the migration before
   - The script will skip the migration safely

3. **Permission Error:**
   - Ensure your database user has ALTER TABLE permissions
   - Contact your database administrator if needed

## Rollback (if needed)

If you need to remove the column:

```sql
ALTER TABLE "user" DROP COLUMN sector_changed_at;
```

## Feature Details

After this migration, the weekly sector change restriction will work as follows:

- **Basic users** can change their sector once per week
- **Premium/Max users** are unaffected (no restrictions)
- **First-time basic users** can select any sector initially
- **Dashboard** shows countdown when change is restricted

## Support

If you encounter any issues:

1. Check the error messages in the migration output
2. Verify your database connection settings
3. Ensure you have the necessary database permissions
4. Contact support if problems persist 