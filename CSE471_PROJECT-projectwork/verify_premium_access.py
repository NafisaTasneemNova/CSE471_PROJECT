#!/usr/bin/env python3
"""
Script to verify if a user's premium subscription is properly set in the database.
This helps troubleshoot access issues after purchasing premium.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def verify_premium_access():
    try:
        # Import database after adding to path
        import database
        
        # Initialize database connection
        await database.init_db()
        
        if database.db is None:
            print("❌ Failed to connect to database")
            return
        
        print("🔍 Checking Premium Access Status")
        print("=" * 60)
        
        # Get all companies
        companies = await database.db["companies"].find({}).to_list(length=None)
        
        if not companies:
            print("❌ No companies found in database")
            return
        
        # Find premium users
        premium_users = []
        free_users = []
        
        for company in companies:
            name = company.get('name', 'Unknown')
            tier = company.get('subscription_tier', 'FREE')
            company_id = company.get('id', 'N/A')
            expires_at = company.get('subscription_expires_at')
            
            if tier == 'PREMIUM':
                premium_users.append({
                    'name': name,
                    'id': company_id,
                    'expires_at': expires_at
                })
            else:
                free_users.append({
                    'name': name,
                    'id': company_id
                })
        
        # Display results
        if premium_users:
            print(f"\n✅ PREMIUM Users ({len(premium_users)}):")
            print("-" * 60)
            for user in premium_users:
                print(f"  Company: {user['name']}")
                print(f"  ID: {user['id']}")
                if user['expires_at']:
                    if isinstance(user['expires_at'], str):
                        expires_at = datetime.fromisoformat(user['expires_at'])
                    else:
                        expires_at = user['expires_at']
                    
                    days_left = (expires_at - datetime.utcnow()).days
                    if days_left > 0:
                        print(f"  ✅ Status: ACTIVE (expires in {days_left} days)")
                        print(f"  📅 Expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                    else:
                        print(f"  ⚠️  Status: EXPIRED ({abs(days_left)} days ago)")
                else:
                    print(f"  ⚠️  Status: ACTIVE (no expiry set)")
                print()
        else:
            print("\n⚠️  No PREMIUM users found!")
            print("   This might be why you can't access the auction.")
        
        if free_users:
            print(f"\n🆓 FREE Users ({len(free_users)}):")
            print("-" * 60)
            for user in free_users:
                print(f"  • {user['name']} (ID: {user['id']})")
        
        print("\n" + "=" * 60)
        
        # Provide troubleshooting steps
        if not premium_users:
            print("\n🔧 TROUBLESHOOTING:")
            print("   Your subscription might not have been updated in the database.")
            print("\n   Solutions:")
            print("   1. Run: python upgrade_to_premium.py")
            print("   2. Or manually update via MongoDB:")
            print("      db.companies.updateOne(")
            print("        { name: 'YourCompanyName' },")
            print("        { $set: { subscription_tier: 'PREMIUM' } }")
            print("      )")
        else:
            print("\n✅ Database looks correct!")
            print("\n   If you still can't access auctions:")
            print("   1. Log out and log back in")
            print("   2. Clear browser cache (Ctrl+Shift+Delete)")
            print("   3. Try in incognito/private mode")
            print("   4. Check browser console for errors (F12)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close database connection
        if hasattr(database, 'client') and database.client:
            database.client.close()

if __name__ == "__main__":
    asyncio.run(verify_premium_access())