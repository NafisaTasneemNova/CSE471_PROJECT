"""
Script to fix subscription dates for existing users.
Run this once to reset all users' subscription locks.
"""
import asyncio
from database import connect_to_mongo, close_mongo_connection, db

async def fix_subscriptions():
    """Reset subscription_can_change_after to None for all users."""
    await connect_to_mongo()
    
    if db is not None:
        # Update all companies to have None for subscription dates
        result = await db["companies"].update_many(
            {},  # Match all documents
            {"$set": {
                "subscription_start_date": None,
                "subscription_can_change_after": None
            }}
        )
        
        print(f"✅ Updated {result.modified_count} companies")
        print("All users can now select their subscription plan!")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(fix_subscriptions())
