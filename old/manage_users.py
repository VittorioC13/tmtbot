#!/usr/bin/env python3
"""
User Management Script for TMT API
Check and manage users and their payment status in the database
"""
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from index import app, db, User

def list_all_users():
    """List all users in the database"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in the database.")
            return
        
        print(f"\n📊 Found {len(users)} users:")
        print("=" * 80)
        print(f"{'ID':<5} {'Username':<20} {'Payment Status':<15} {'Created Date':<20}")
        print("-" * 80)
        
        for user in users:
            status = "✅ PAID" if user.is_paid else "❌ UNPAID"
            print(f"{user.id:<5} {user.username:<20} {status:<15} {user.id}")  # Using ID as proxy for date
        
        print("-" * 80)

def check_user_status(user_id):
    """Check specific user's status"""
    with app.app_context():
        user = User.query.get(user_id)
        
        if not user:
            print(f"❌ User with ID {user_id} not found.")
            return
        
        print(f"\n👤 User Details:")
        print("=" * 40)
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Payment Status: {'✅ PAID' if user.is_paid else '❌ UNPAID'}")
        print(f"Password Hash: {user.password[:20]}...")

def update_user_payment_status(user_id, is_paid):
    """Update user's payment status"""
    with app.app_context():
        user = User.query.get(user_id)
        
        if not user:
            print(f"❌ User with ID {user_id} not found.")
            return
        
        old_status = user.is_paid
        user.is_paid = is_paid
        db.session.commit()
        
        print(f"✅ Updated user {user.username} (ID: {user.id})")
        print(f"Payment status changed from {'PAID' if old_status else 'UNPAID'} to {'PAID' if is_paid else 'UNPAID'}")

def create_user(username, password, is_paid=False):
    """Create a new user"""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists.")
            return
        
        # Create new user
        user = User()
        user.username = username
        user.password = password
        user.is_paid = is_paid
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Created user '{username}' with ID {user.id}")
        print(f"Payment status: {'PAID' if is_paid else 'UNPAID'}")

def delete_user(user_id):
    """Delete a user"""
    with app.app_context():
        user = User.query.get(user_id)
        
        if not user:
            print(f"❌ User with ID {user_id} not found.")
            return
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        print(f"✅ Deleted user '{username}' (ID: {user_id})")

def get_payment_statistics():
    """Get payment statistics"""
    with app.app_context():
        total_users = User.query.count()
        paid_users = User.query.filter_by(is_paid=True).count()
        unpaid_users = User.query.filter_by(is_paid=False).count()
        
        print(f"\n📈 Payment Statistics:")
        print("=" * 30)
        print(f"Total Users: {total_users}")
        print(f"Paid Users: {paid_users}")
        print(f"Unpaid Users: {unpaid_users}")
        
        if total_users > 0:
            paid_percentage = (paid_users / total_users) * 100
            print(f"Paid Percentage: {paid_percentage:.1f}%")

def search_users(search_term):
    """Search users by username"""
    with app.app_context():
        users = User.query.filter(User.username.contains(search_term)).all()
        
        if not users:
            print(f"No users found matching '{search_term}'.")
            return
        
        print(f"\n🔍 Found {len(users)} users matching '{search_term}':")
        print("=" * 60)
        print(f"{'ID':<5} {'Username':<20} {'Payment Status':<15}")
        print("-" * 60)
        
        for user in users:
            status = "✅ PAID" if user.is_paid else "❌ UNPAID"
            print(f"{user.id:<5} {user.username:<20} {status:<15}")

def show_menu():
    """Show the main menu"""
    print("\n" + "=" * 50)
    print("TMT API User Management Tool")
    print("=" * 50)
    print("1. List all users")
    print("2. Check specific user status")
    print("3. Update user payment status")
    print("4. Create new user")
    print("5. Delete user")
    print("6. Get payment statistics")
    print("7. Search users")
    print("8. Exit")
    print("=" * 50)

def main():
    """Main function with interactive menu"""
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            list_all_users()
            
        elif choice == "2":
            user_id = input("Enter user ID: ").strip()
            try:
                check_user_status(int(user_id))
            except ValueError:
                print("❌ Invalid user ID. Please enter a number.")
                
        elif choice == "3":
            user_id = input("Enter user ID: ").strip()
            status = input("Enter payment status (paid/unpaid): ").strip().lower()
            
            try:
                is_paid = status == "paid"
                update_user_payment_status(int(user_id), is_paid)
            except ValueError:
                print("❌ Invalid user ID. Please enter a number.")
                
        elif choice == "4":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            is_paid = input("Is user paid? (y/n): ").strip().lower() == "y"
            create_user(username, password, is_paid)
            
        elif choice == "5":
            user_id = input("Enter user ID to delete: ").strip()
            confirm = input("Are you sure? (y/n): ").strip().lower()
            
            if confirm == "y":
                try:
                    delete_user(int(user_id))
                except ValueError:
                    print("❌ Invalid user ID. Please enter a number.")
            else:
                print("❌ Deletion cancelled.")
                
        elif choice == "6":
            get_payment_statistics()
            
        elif choice == "7":
            search_term = input("Enter search term: ").strip()
            search_users(search_term)
            
        elif choice == "8":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter a number between 1-8.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Check if database is accessible
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your DATABASE_URL environment variable.")
        sys.exit(1)
    
    main() 