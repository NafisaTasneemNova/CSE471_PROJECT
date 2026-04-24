"""
Utility script to check and fix the bids collection in MongoDB.
This script will:
1. Check for any unique indexes that might cause bid overwrites
2. Remove problematic indexes
3. Verify that multiple bids from the same supplier are stored correctly
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = "texbid_db"

async def check_and_fix_bids():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    print("=" * 60)
    print("CHECKING BIDS COLLECTION")
    print("=" * 60)
    
    # Check existing indexes
    print("\n1. Checking existing indexes on 'bids' collection...")
    indexes = await db["bids"].list_indexes().to_list(length=None)
    
    print(f"   Found {len(indexes)} index(es):")
    for idx in indexes:
        print(f"   - {idx['name']}: {idx.get('key', {})}")
        if idx.get('unique', False):
            print(f"     ⚠️  WARNING: This is a UNIQUE index!")
    
    # Check for problematic unique indexes
    problematic_indexes = []
    for idx in indexes:
        if idx.get('unique', False) and idx['name'] != '_id_':
            # Check if it's on supplier_id or a combination that would prevent multiple bids
            key_fields = list(idx.get('key', {}).keys())
            if any(field in ['supplier_id', 'supplier_name'] for field in key_fields):
                problematic_indexes.append(idx['name'])
    
    if problematic_indexes:
        print(f"\n2. Found {len(problematic_indexes)} problematic unique index(es):")
        for idx_name in problematic_indexes:
            print(f"   - {idx_name}")
        
        response = input("\n   Do you want to DROP these indexes? (yes/no): ")
        if response.lower() == 'yes':
            for idx_name in problematic_indexes:
                await db["bids"].drop_index(idx_name)
                print(f"   ✅ Dropped index: {idx_name}")
        else:
            print("   Skipped dropping indexes.")
    else:
        print("\n2. ✅ No problematic unique indexes found!")
    
    # Check current bids
    print("\n3. Checking current bids in the collection...")
    bid_count = await db["bids"].count_documents({})
    print(f"   Total bids: {bid_count}")
    
    if bid_count > 0:
        # Group by supplier to see if there are multiple bids per supplier
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "supplier_id": "$supplier_id",
                        "supplier_name": "$supplier_name",
                        "rfq_id": "$rfq_id"
                    },
                    "bid_count": {"$sum": 1},
                    "bids": {"$push": {"price": "$bid_price", "timestamp": "$timestamp"}}
                }
            },
            {"$match": {"bid_count": {"$gt": 1}}}
        ]
        
        multiple_bids = await db["bids"].aggregate(pipeline).to_list(length=None)
        
        if multiple_bids:
            print(f"\n   ✅ Found {len(multiple_bids)} supplier(s) with multiple bids:")
            for item in multiple_bids:
                supplier_info = item['_id']
                print(f"   - Supplier: {supplier_info['supplier_name']} (ID: {supplier_info['supplier_id']})")
                print(f"     RFQ: {supplier_info['rfq_id']}")
                print(f"     Number of bids: {item['bid_count']}")
                for i, bid in enumerate(item['bids'], 1):
                    print(f"       Bid {i}: ${bid['price']:.2f} at {bid['timestamp']}")
        else:
            print("   ℹ️  No suppliers with multiple bids found (each supplier has only 1 bid per RFQ)")
    
    # Show sample bids
    print("\n4. Sample bids (last 5):")
    sample_bids = await db["bids"].find().sort("timestamp", -1).limit(5).to_list(length=5)
    for bid in sample_bids:
        print(f"   - {bid.get('supplier_name', 'N/A')} (ID: {bid.get('supplier_id', 'N/A')})")
        print(f"     Price: ${bid.get('bid_price', 0):.2f}, Time: {bid.get('timestamp', 'N/A')}")
        print(f"     Bid ID: {bid.get('id', 'N/A')}, MongoDB _id: {bid.get('_id', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_and_fix_bids())
