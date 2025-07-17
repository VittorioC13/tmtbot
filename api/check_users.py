#!/usr/bin/env python3
"""
Script to check the current state of users in the database
"""

import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def check_users():
    """Check the current state of all users"""
    with app.app_context():
        try:
            users = User.query.all()
            
            print(f"📊 Found {len(users)} users in database:")
            print("-" * 80)
            
            for user in users:
                status = "✅ Premium" if user.has_valid_premium else "❌ No Access"
                expires = user.premium_expires_at.strftime('%Y-%m-%d %H:%M') if user.premium_expires_at else "NULL"
                
                print(f"User: {user.username}")
                print(f"  ID: {user.id}")
                print(f"  is_paid: {user.is_paid}")
                print(f"  premium_expires_at: {expires}")
                print(f"  has_valid_premium: {user.has_valid_premium}")
                print(f"  Status: {status}")
                print("-" * 40)
            
        except Exception as e:
            print(f"❌ Error checking users: {e}")

if __name__ == "__main__":
    print("🔍 Checking user database state...")
    check_users()
    print("✅ Check completed!") 