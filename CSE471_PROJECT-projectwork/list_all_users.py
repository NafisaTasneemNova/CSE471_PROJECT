#!/usr/bin/env python3
"""
List all users in the system with their credentials info.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def list_users():
    try:
        import database
        
        await database.init_db()
        
        if database.db is None:
            print("❌ Failed to connect to database")
            return
        
        print("👥 ALL USERS IN SYSTEM")
        print("=" * 70)
        
        # Get all users
        users = await database.db["users"].find({}).to_list(length=None)
        
        if not users:
            print("❌ No users found in database")
            print("\n💡 You need to register a user first:")
            print("   Go to: http://localhost:8000/register")
            return
        
        print(f"\nFound {len(users)} user(s):\n")
        
        for i, user in enumerate(users, 1):
            email = user.get('email', 'N/A')
            user_id = user.get('id', 'N/A')
            is_admin = user.get('is_admin', False)
            company_id = user.get('company_id', 'N/A')
            
            # Get company info
            company = None
            if company_id != 'N/A':
                company = await database.db["companies"].find_one({"id": company_id})
            
            print(f"{i}. Email: {email}")
            print(f"   User ID: {user_id}")
            print(f"   Admin: {'✅ YES' if is_admin else '❌ NO'}")
            
            if company:
                company_name = company.get('name', 'Unknown')
                tier = company.get('subscription_tier', 'FREE')
                print(f"   Company: {company_name}")
                print(f"   Subscription: {tier}")
            else:
                print(f"   Company: Not found")
            
            print()
        
        print("=" * 70)
        print("\n📝 IMPORTANT NOTES:")
        print("   • Passwords are hashed in the database (cannot be retrieved)")
        print("   • You need to know your password to log in")
        print("   • If you forgot your password, you'll need to reset it")
        
        # Check for admins
        admins = [u for u in users if u.get('is_admin') == True]
        
        if admins:
            print(f"\n👑 ADMIN ACCOUNTS ({len(admins)}):")
            for admin in admins:
                print(f"   • {admin.get('email', 'N/A')}")
            print("\n✅ You can log in with any of these admin accounts")
            print("   (You need to know the password)")
        else:
            print("\n⚠️  NO ADMIN ACCOUNTS FOUND!")
            print("\n💡 TO CREATE AN ADMIN:")
            print("   1. Run: python make_user_admin.py")
            print("   2. Select a user to make admin")
            print("   3. Log in with that user's credentials")
        
        print("\n🌐 LOGIN PAGE:")
        print("   http://localhost:8000/login")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hasattr(database, 'client') and database.client:
            database.client.close()

if __name__ == "__main__":
    asyncio.run(list_users())