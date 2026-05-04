#!/usr/bin/env python3
"""
Create a new admin user with specified credentials.
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def create_admin():
    try:
        import database
        from passlib.context import CryptContext
        
        # Password hashing
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        await database.init_db()
        
        if database.db is None:
            print("❌ Failed to connect to database")
            return
        
        print("👑 CREATE NEW ADMIN USER")
        print("=" * 70)
        
        # Get user input
        email = input("\n📧 Enter email address: ").strip()
        
        if not email or '@' not in email:
            print("❌ Invalid email address")
            return
        
        # Check if email already exists
        existing_user = await database.db["users"].find_one({"email": email})
        if existing_user:
            print(f"\n⚠️  User with email '{email}' already exists!")
            make_admin = input("   Make this user an admin? (yes/no): ").lower()
            if make_admin in ['yes', 'y']:
                result = await database.db["users"].update_one(
                    {"email": email},
                    {"$set": {"is_admin": True}}
                )
                if result.modified_count > 0:
                    print(f"\n✅ '{email}' is now an admin!")
                    print(f"\n🌐 Log in at: http://localhost:8000/login")
                    print(f"   Email: {email}")
                    print(f"   Password: (your existing password)")
                else:
                    print(f"\n✅ '{email}' is already an admin!")
            return
        
        password = input("🔒 Enter password: ").strip()
        
        if len(password) < 6:
            print("❌ Password must be at least 6 characters")
            return
        
        company_name = input("🏢 Enter company name: ").strip()
        
        if not company_name:
            company_name = f"{email.split('@')[0]}'s Company"
        
        # Create company
        company_id = str(uuid.uuid4())
        company = {
            "id": company_id,
            "name": company_name,
            "role": "BUYER",  # Default role
            "subscription_tier": "PREMIUM",  # Give admin PREMIUM by default
            "subscription_start_date": datetime.utcnow(),
            "subscription_expires_at": None,  # No expiry for admin
            "created_at": datetime.utcnow()
        }
        
        await database.db["companies"].insert_one(company)
        print(f"\n✅ Created company: {company_name}")
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = pwd_context.hash(password)
        
        user = {
            "id": user_id,
            "email": email,
            "hashed_password": hashed_password,
            "company_id": company_id,
            "is_admin": True,  # Make admin
            "created_at": datetime.utcnow()
        }
        
        await database.db["users"].insert_one(user)
        print(f"✅ Created admin user: {email}")
        
        print("\n" + "=" * 70)
        print("🎉 SUCCESS! Admin user created!")
        print("\n📋 LOGIN CREDENTIALS:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Company: {company_name}")
        print(f"   Subscription: PREMIUM (no expiry)")
        
        print("\n🌐 LOGIN:")
        print("   1. Go to: http://localhost:8000/login")
        print(f"   2. Email: {email}")
        print(f"   3. Password: {password}")
        
        print("\n🔧 ADMIN PANEL:")
        print("   After login, go to:")
        print("   • http://localhost:8000/admin/subscriptions")
        print("   • http://localhost:8000/admin/dashboard")
        
        print("\n⚠️  SAVE THESE CREDENTIALS!")
        print("   Write them down or save to a password manager")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hasattr(database, 'client') and database.client:
            database.client.close()

if __name__ == "__main__":
    asyncio.run(create_admin())