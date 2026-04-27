"""
Quick script to make yourself an admin.
Just run: python quick_admin.py
"""

import asyncio
from database import db, connect_to_mongo

async def make_admin():
    await connect_to_mongo()
    
    if db is None:
        print("❌ Database connection failed")
        return
    
    # Ask for email
    email = input("Enter your email address: ").strip()
    
    # Find user
    user = await db["users"].find_one({"email": email})
    
    if not user:
        print(f"❌ User not found: {email}")
        print("Please register first at http://localhost:8000/register")
        return
    
    # Make admin
    result = await db["users"].update_one(
        {"email": email},
        {"$set": {"is_admin": True}}
    )
    
    if result.modified_count > 0:
        print(f"✅ SUCCESS! {email} is now an admin!")
        print(f"🔐 You can now login at: http://localhost:8000/admin/login")
    else:
        print(f"ℹ️  {email} was already an admin")
        print(f"🔐 Login at: http://localhost:8000/admin/login")

if __name__ == "__main__":
    asyncio.run(make_admin())
