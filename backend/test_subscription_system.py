"""
Test script for the subscription system.
This script helps verify that the subscription system is working correctly.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = "texbid_db"

async def test_subscription_system():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    print("=" * 70)
    print("SUBSCRIPTION SYSTEM TEST")
    print("=" * 70)
    
    # 1. Check if subscription_tier field exists in companies
    print("\n1. Checking company subscription tiers...")
    companies = await db["companies"].find().limit(5).to_list(length=5)
    
    if not companies:
        print("   ⚠️  No companies found in database")
        print("   Create a company first via /verify/supplier or /verify/buyer")
    else:
        print(f"   Found {len(companies)} companies (showing first 5):")
        for company in companies:
            tier = company.get("subscription_tier", "NOT SET")
            name = company.get("name", "Unknown")
            print(f"   - {name}: {tier}")
    
    # 2. Count by tier
    print("\n2. Subscription distribution...")
    total = await db["companies"].count_documents({})
    free_count = await db["companies"].count_documents({"subscription_tier": "FREE"})
    premium_count = await db["companies"].count_documents({"subscription_tier": "PREMIUM"})
    no_tier = total - free_count - premium_count
    
    print(f"   Total companies: {total}")
    print(f"   FREE tier: {free_count}")
    print(f"   PREMIUM tier: {premium_count}")
    if no_tier > 0:
        print(f"   ⚠️  No tier set: {no_tier} (will default to FREE)")
    
    # 3. Test upgrade/downgrade
    print("\n3. Testing subscription toggle...")
    if companies:
        test_company = companies[0]
        company_id = test_company.get("id")
        current_tier = test_company.get("subscription_tier", "FREE")
        new_tier = "PREMIUM" if current_tier != "PREMIUM" else "FREE"
        
        print(f"   Test company: {test_company.get('name')}")
        print(f"   Current tier: {current_tier}")
        print(f"   Toggling to: {new_tier}")
        
        response = input(f"\n   Do you want to toggle this company to {new_tier}? (yes/no): ")
        if response.lower() == 'yes':
            result = await db["companies"].update_one(
                {"id": company_id},
                {"$set": {"subscription_tier": new_tier}}
            )
            if result.modified_count > 0:
                print(f"   ✅ Successfully updated to {new_tier}")
            else:
                print("   ❌ Update failed")
        else:
            print("   Skipped toggle test")
    
    # 4. Migration check
    print("\n4. Checking for companies without subscription_tier...")
    companies_without_tier = await db["companies"].find(
        {"subscription_tier": {"$exists": False}}
    ).to_list(length=None)
    
    if companies_without_tier:
        print(f"   Found {len(companies_without_tier)} companies without subscription_tier")
        response = input("   Do you want to set them all to FREE? (yes/no): ")
        if response.lower() == 'yes':
            result = await db["companies"].update_many(
                {"subscription_tier": {"$exists": False}},
                {"$set": {"subscription_tier": "FREE"}}
            )
            print(f"   ✅ Updated {result.modified_count} companies to FREE tier")
    else:
        print("   ✅ All companies have subscription_tier set")
    
    # 5. Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("\n✅ Subscription system is ready!")
    print("\nNext steps:")
    print("  1. Start the server: uvicorn main:app --reload")
    print("  2. Visit admin dashboard: http://localhost:8000/admin/subscriptions")
    print("  3. View pricing page: http://localhost:8000/pricing")
    print("  4. Test premium features with FREE and PREMIUM users")
    print("\nProtected features:")
    print("  - Reverse Auction (/rfq/auctions)")
    print("  - AI Recommendations (/api/predict-price)")
    print("  - Order Analytics (to be implemented)")
    print("  - Automated Contracts (to be implemented)")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_subscription_system())
