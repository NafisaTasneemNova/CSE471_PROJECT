#!/usr/bin/env python3
"""
Check which users have admin access in the system.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def check_admins():
    try:
        import database
        
        await database.init_db()
        
        if database.db is None:
            print("❌ Failed to connect to database")
            return
        
        print("🔍 Checking Admin Users")
        print("=" * 60)
        
        # Get all users
        users = await database.db["users"].find({}).to_list(length=None)
        
        if not users:
            print("❌ No users found in database")
            return
        
        # Find admins
        admins = [u for u in users if u.get('is_admin') == True]
        non_admins = [u for u in users if not u.get('is_admin')]
        
        if admins:
            print(f"\n👑 ADMIN USERS ({len(admins)}):")
            print("-" * 60)
            for admin in admins:
                email = admin.get('email', 'N/A')
                user_id = admin.get('id', 'N/A')
                print(f"  ✅ {email}")
                print(f"     User ID: {user_id}")
                print()
        else:
            print("\n⚠️  NO ADMIN USERS FOUND!")
            print("   You need to make a user an admin first.")
        
        if non_admins:
            print(f"\n👤 REGULAR USERS ({len(non_admins)}):")
            print("-" * 60)
            for user in non_admins:
                email = user.get('email', 'N/A')
                user_id = user.get('id', 'N/A')
                print(f"  • {email} (ID: {user_id})")
        
        print("\n" + "=" * 60)
        
        if not admins:
            print("\n💡 TO MAKE A USER AN ADMIN:")
            print("   Run: python make_admin.py")
            print("   Or manually update MongoDB:")
            print("   db.users.updateOne(")
            print("     { email: 'your@email.com' },")
            print("     { $set: { is_admin: true } }")
            print("   )")
        else:
            print("\n🌐 ADMIN PAGE ACCESS:")
            print("   1. Log in as an admin user")
            print("   2. Go to: http://localhost:8000/admin/subscriptions")
            print("   3. Or: http://localhost:8000/admin/dashboard")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hasattr(database, 'client') and database.client:
            database.client.close()

if __name__ == "__main__":
    asyncio.run(check_admins())