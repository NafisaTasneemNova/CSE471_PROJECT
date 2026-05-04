#!/usr/bin/env python3
"""
Comprehensive diagnostic script to troubleshoot Reverse Auction access issues.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def diagnose_access():
    try:
        import database
        
        await database.init_db()
        
        if database.db is None:
            print("❌ Failed to connect to database")
            return
        
        print("🔍 REVERSE AUCTION ACCESS DIAGNOSTIC")
        print("=" * 70)
        
        # Step 1: Check all users
        print("\n📋 STEP 1: Checking all registered users...")
        users = await database.db["users"].find({}).to_list(length=None)
        print(f"   Found {len(users)} users")
        
        # Step 2: Check all companies
        print("\n🏢 STEP 2: Checking all companies...")
        companies = await database.db["companies"].find({}).to_list(length=None)
        print(f"   Found {len(companies)} companies")
        
        # Step 3: Match users to companies and check subscriptions
        print("\n🔗 STEP 3: User-Company-Subscription Mapping:")
        print("-" * 70)
        
        for user in users:
            email = user.get('email', 'N/A')
            user_id = user.get('id', 'N/A')
            company_id = user.get('company_id', 'N/A')
            
            # Find associated company
            company = next((c for c in companies if c.get('id') == company_id), None)
            
            if company:
                company_name = company.get('name', 'Unknown')
                tier = company.get('subscription_tier', 'FREE')
                expires_at = company.get('subscription_expires_at')
                
                print(f"\n👤 User: {email}")
                print(f"   User ID: {user_id}")
                print(f"   Company: {company_name}")
                print(f"   Company ID: {company_id}")
                print(f"   Subscription: {tier}")
                
                if tier == 'PREMIUM':
                    if expires_at:
                        if isinstance(expires_at, str):
                            expires_at = datetime.fromisoformat(expires_at)
                        days_left = (expires_at - datetime.utcnow()).days
                        
                        if days_left > 0:
                            print(f"   ✅ Status: ACTIVE")
                            print(f"   📅 Expires in: {days_left} days")
                            print(f"   🎯 CAN ACCESS REVERSE AUCTION: YES")
                        else:
                            print(f"   ⚠️  Status: EXPIRED ({abs(days_left)} days ago)")
                            print(f"   🎯 CAN ACCESS REVERSE AUCTION: NO")
                    else:
                        print(f"   ✅ Status: ACTIVE (no expiry)")
                        print(f"   🎯 CAN ACCESS REVERSE AUCTION: YES")
                else:
                    print(f"   🆓 Status: FREE PLAN")
                    print(f"   🎯 CAN ACCESS REVERSE AUCTION: NO")
            else:
                print(f"\n👤 User: {email}")
                print(f"   ⚠️  No company found for company_id: {company_id}")
                print(f"   🎯 CAN ACCESS REVERSE AUCTION: NO")
        
        # Step 4: Summary and recommendations
        print("\n" + "=" * 70)
        print("📊 SUMMARY:")
        
        premium_count = sum(1 for c in companies if c.get('subscription_tier') == 'PREMIUM')
        free_count = len(companies) - premium_count
        
        print(f"   Total Companies: {len(companies)}")
        print(f"   PREMIUM: {premium_count}")
        print(f"   FREE: {free_count}")
        
        if premium_count == 0:
            print("\n❌ PROBLEM IDENTIFIED:")
            print("   No companies have PREMIUM subscription!")
            print("\n💡 SOLUTION:")
            print("   Run: python upgrade_to_premium.py")
            print("   This will upgrade a company to PREMIUM.")
        else:
            print("\n✅ Database has PREMIUM users!")
            print("\n🔧 IF YOU STILL CAN'T ACCESS:")
            print("   1. Make sure you're logged in as the correct user")
            print("   2. Log out and log back in to refresh your session")
            print("   3. Clear browser cache (Ctrl+Shift+Delete)")
            print("   4. Try in incognito/private browsing mode")
            print("   5. Check browser console (F12) for JavaScript errors")
        
        # Step 5: Provide direct access test
        print("\n" + "=" * 70)
        print("🧪 QUICK TEST:")
        print("   After logging in, try accessing:")
        print("   http://localhost:8000/rfq/auctions")
        print("\n   Expected behavior:")
        print("   • FREE user: See 'Premium Required' page")
        print("   • PREMIUM user: See auction list page")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hasattr(database, 'client') and database.client:
            database.client.close()

if __name__ == "__main__":
    asyncio.run(diagnose_access())