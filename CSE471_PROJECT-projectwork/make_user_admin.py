#!/usr/bin/env python3
"""
Make a user an admin so they can access the admin panel.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def make_admin():
    try:
        import database
        
        # Connect to database
        await database.connect_to_mongo()
        
        if database.db is None:
            print("❌ Failed to connect to database")
            return
        
        print("👑 Make User Admin")
        print("=" * 60)
        
        # Get all users
        users = await database.db["users"].find({}).to_list(length=None)
        
        if not users:
            print("❌ No users found in database")
            return
        
        print("\n📋 Available users:")
        for i, user in enumerate(users):
            email = user.get('email', 'Unknown')
            is_admin = user.get('is_admin', False)
            status = "👑 ADMIN" if is_admin else "👤 Regular"
            print(f"  {i+1}. {email} - {status}")
        
        # Get user choice
        try:
            choice = int(input("\n🔢 Enter user number to make admin: ")) - 1
            if choice < 0 or choice >= len(users):
                print("❌ Invalid choice")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        selected_user = users[choice]
        email = selected_user.get('email', 'Unknown')
        
        # Check if already admin
        if selected_user.get('is_admin') == True:
            print(f"\n✅ {email} is already an admin!")
            return
        
        # Confirm
        confirm = input(f"\n⚠️  Make '{email}' an admin? (yes/no): ").lower()
        if confirm not in ['yes', 'y']:
            print("❌ Cancelled")
            return
        
        # Update user to admin
        result = await database.db["users"].update_one(
            {"id": selected_user["id"]},
            {"$set": {"is_admin": True}}
        )
        
        if result.modified_count > 0:
            print(f"\n✅ SUCCESS! '{email}' is now an admin!")
            print("\n🌐 Admin Panel Access:")
            print("   1. Log out and log back in as this user")
            print("   2. Go to: http://localhost:8000/admin/subscriptions")
            print("   3. Or: http://localhost:8000/admin/dashboard")
            print("\n💡 From the admin panel, you can:")
            print("   • Toggle user subscriptions (FREE ↔ PREMIUM)")
            print("   • View all companies and their subscription status")
            print("   • Manage user accounts")
        else:
            print(f"❌ Failed to update '{email}'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hasattr(database, 'client') and database.client:
            await database.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(make_admin())