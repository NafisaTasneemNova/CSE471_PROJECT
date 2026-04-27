"""
Super simple admin maker - uses pymongo directly
"""

from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["texbid_db"]

# Ask for email
email = input("Enter your email address: ").strip()

# Find user
user = db["users"].find_one({"email": email})

if not user:
    print(f"❌ User not found: {email}")
    print("Please register first at http://localhost:8000/register")
else:
    # Make admin
    result = db["users"].update_one(
        {"email": email},
        {"$set": {"is_admin": True}}
    )
    
    if result.modified_count > 0:
        print(f"✅ SUCCESS! {email} is now an admin!")
    else:
        print(f"ℹ️  {email} was already an admin")
    
    print(f"🔐 Login at: http://localhost:8000/admin/login")

client.close()
