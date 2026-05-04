#!/usr/bin/env python3
"""
Script to check current subscription status of all users.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def check_subscriptions():
    try:
        # Import database after adding to path
        import database
        
        # Initialize database connection
        await database.init_db()
        
        if database.db is None:
            print("❌ Failed to connect to database")
            return
        
        # Get all companies with their subscription info
        companies = await database.db["companies"].find({}).to_list(length=None)
        
        if not companies:
            print("❌ No companies found in database")
            return
        
        print("📊 Current Subscription Status:")
        print("=" * 60)
        
        free_count = 0
        premium_count = 0
        
        for company in companies:
            name = company.get('name', 'Unknown')
            tier = company.get('subscription_tier', 'FREE')
            expires_at = company.get('subscription_expires_at')
            
            if tier == 'FREE':
                free_count += 1
                print(f"🆓 {name:<30} | FREE")
            else:
                premium_count += 1
                if expires_at:
                    if isinstance(expires_at, str):
                        expires_at = datetime.fromisoformat(expires_at)
                    days_left = (expires_at - datetime.utcnow()).days
                    if days_left > 0:
                        print(f"⭐ {name:<30} | PREMIUM (expires in {days_left} days)")
                    else:
                        print(f"⚠️  {name:<30} | PREMIUM (EXPIRED)")
                else:
                    print(f"⭐ {name:<30} | PREMIUM (no expiry set)")
        
        print("=" * 60)
        print(f"📈 Summary: {free_count} FREE, {premium_count} PREMIUM")
        
        if premium_count == 0:
            print("\n💡 To access Reverse Auctions, upgrade to PREMIUM:")
            print("   1. Run: python upgrade_to_premium.py")
            print("   2. Or visit: http://localhost:8000/pricing")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Close database connection
        if hasattr(database, 'client') and database.client:
            database.client.close()

if __name__ == "__main__":
    print("🔍 TexBid Subscription Checker")
    print("=" * 40)
    asyncio.run(check_subscriptions())