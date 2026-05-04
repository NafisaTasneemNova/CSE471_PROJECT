#!/usr/bin/env python3
"""
Quick script to upgrade a user to PREMIUM subscription for testing purposes.
Run this script to manually upgrade the current user to PREMIUM.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def upgrade_user_to_premium():
    try:
        # Import database after adding to path
        import database
        
        # Initialize database connection
        await database.init_db()
        
        if database.db is None:
            print("❌ Failed to connect to database")
            return
        
        # Get all companies
        companies = await database.db["companies"].find({}).to_list(length=None)
        
        if not companies:
            print("❌ No companies found in database")
            return
        
        print("📋 Available companies:")
        for i, company in enumerate(companies):
            current_tier = company.get('subscription_tier', 'FREE')
            print(f"  {i+1}. {company.get('name', 'Unknown')} - Current: {current_tier}")
        
        # Get user choice
        try:
            choice = int(input("\n🔢 Enter company number to upgrade to PREMIUM: ")) - 1
            if choice < 0 or choice >= len(companies):
                print("❌ Invalid choice")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        selected_company = companies[choice]
        company_name = selected_company.get('name', 'Unknown')
        
        # Calculate expiry date (30 days from now)
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Update the company to PREMIUM
        result = await database.db["companies"].update_one(
            {"id": selected_company["id"]},
            {
                "$set": {
                    "subscription_tier": "PREMIUM",
                    "subscription_expires_at": expires_at,
                    "subscription_start_date": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Successfully upgraded '{company_name}' to PREMIUM!")
            print(f"📅 Expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"🎯 You can now access Reverse Auctions at: http://localhost:8000/rfq/auctions")
        else:
            print(f"❌ Failed to upgrade '{company_name}'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Close database connection
        if hasattr(database, 'client') and database.client:
            database.client.close()

if __name__ == "__main__":
    print("🚀 TexBid Premium Upgrade Tool")
    print("=" * 40)
    asyncio.run(upgrade_user_to_premium())