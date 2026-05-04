import asyncio
import uuid
import hashlib
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

def hash_password(password: str) -> str:
    """Hash password for storage."""
    return hashlib.sha256(password.encode()).hexdigest()

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.texbid_db
    
    email = "admin@texbid"
    password = "admin1234!"
    
    user = await db.users.find_one({"email": email})
    
    if user:
        # Update existing user
        await db.users.update_one(
            {"_id": user["_id"]}, 
            {
                "$set": {
                    "is_admin": True,
                    "password_hash": hash_password(password)
                }
            }
        )
        print(f"Updated existing user {email} to be an admin with the new password.")
    else:
        # Create new user
        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "email": email,
            "password_hash": hash_password(password),
            "role": "BUYER",  # Just default
            "is_admin": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.users.insert_one(new_user)
        print(f"Created new admin user {email} with password {password}")

asyncio.run(main())
