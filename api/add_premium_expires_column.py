#!/usr/bin/env python3
"""
Script to add premium_expires_at column to existing database
Run this script to update the database schema
"""

import os
import sys
from datetime import datetime
from sqlalchemy import text

# Add the current directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def add_premium_expires_column():
    """Add premium_expires_at column to the user table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'premium_expires_at'
            """))
            
            if result.fetchone():
                print("✅ Column 'premium_expires_at' already exists")
                return
            
            # Add the column
            db.session.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN premium_expires_at TIMESTAMP
            """))
            
            db.session.commit()
            print("✅ Successfully added 'premium_expires_at' column to user table")
            
        except Exception as e:
            print(f"❌ Error adding column: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    print("🔄 Adding premium_expires_at column to database...")
    add_premium_expires_column()
    print("✅ Database migration completed!") 