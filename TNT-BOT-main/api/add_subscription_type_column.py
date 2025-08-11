#!/usr/bin/env python3
"""
Script to add subscription_type column to existing database
Run this script to update the database schema
"""

import os
import sys
from datetime import datetime
from sqlalchemy import text

# Add the current directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from index import app, db, User

def add_subscription_type_column():
    """Add subscription_type column to the user table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'subscription_type'
            """))
            
            if result.fetchone():
                print("✅ Column 'subscription_type' already exists")
                return
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN subscription_type VARCHAR(20) DEFAULT 'none'
            """))
            
            db.session.commit()
            print("✅ Successfully added 'subscription_type' column to user table")
            
            # Update existing users based on their current status
            update_existing_users()
            
        except Exception as e:
            print(f"❌ Error adding column: {e}")
            db.session.rollback()
            raise

def update_existing_users():
    """Update existing users to set appropriate subscription_type"""
    try:
        # Find users who have no subscription_type set (legacy users)
        # Note: This script was designed for migration from is_paid to subscription_type
        # Since we've removed is_paid, we'll just check for users with 'none' subscription_type
        legacy_users = User.query.filter(
            User.subscription_type == 'none'
        ).all()
        
        if legacy_users:
            print(f"🔄 Found {len(legacy_users)} legacy users with 'none' subscription_type...")
            print("Note: This migration script is for historical reference only.")
            print("New users will automatically get 'none' subscription_type by default.")
        else:
            print("✅ No legacy users found")
            
    except Exception as e:
        print(f"❌ Error updating existing users: {e}")
        db.session.rollback()

if __name__ == "__main__":
    print("🔄 Adding subscription_type column to database...")
    add_subscription_type_column()
    print("✅ Database migration completed!") 