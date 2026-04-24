"""
Script to make users administrators.
Run this to grant admin access to specific email addresses.
"""

import asyncio
from database import db, connect_to_mongo

# List of admin email addresses
ADMIN_EMAILS = [
    "nova@texbid.com",
    "admin1@texbid.com",
    "admin2@texbid.com",
    "admin3@texbid.com",
    # Add your 4 admin emails here
]


async def make_admins():
    """Make specified users administrators."""
    await connect_to_mongo()
    
    if db is None:
        print("❌ Database connection failed")
        return
    
    print("🔧 Making users administrators...")
    print(f"📧 Admin emails: {', '.join(ADMIN_EMAILS)}")
    print()
    
    for email in ADMIN_EMAILS:
        # Find user
        user = await db["users"].find_one({"email": email})
        
        if user:
            # Update to admin
            result = await db["users"].update_one(
                {"email": email},
                {"$set": {"is_admin": True}}
            )
            
            if result.modified_count > 0:
                print(f"✅ {email} is now an admin")
            else:
                print(f"ℹ️  {email} was already an admin")
        else:
            print(f"⚠️  User not found: {email}")
            print(f"   Please register this email first, then run this script again")
    
    print()
    print("✨ Done! Admins can now log in at: http://localhost:8000/admin/login")


if __name__ == "__main__":
    asyncio.run(make_admins())
