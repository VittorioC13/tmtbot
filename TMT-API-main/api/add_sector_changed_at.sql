-- SQL script to add sector_changed_at column to User table
-- Run this script in your PostgreSQL database

-- Check if column already exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'user' 
        AND column_name = 'sector_changed_at'
    ) THEN
        -- Add the new column
        ALTER TABLE "user" ADD COLUMN sector_changed_at TIMESTAMP;
        
        RAISE NOTICE '✅ Successfully added sector_changed_at column to User table';
    ELSE
        RAISE NOTICE 'ℹ️ Column sector_changed_at already exists. No action needed.';
    END IF;
END $$;

-- Verify the column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name = 'sector_changed_at'; 