"""
Test script to verify that multiple bids from the same supplier are stored correctly.
This script simulates placing multiple bids from the same supplier.
"""

import asyncio
import httpx
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_RFQ_ID = "YOUR_RFQ_ID_HERE"  # Replace with an actual RFQ ID from your database
TEST_SUPPLIER_ID = "TEST_SUP_001"
TEST_SUPPLIER_NAME = "Test Supplier Inc."

async def place_test_bid(bid_price: float, bid_number: int):
    """Place a single test bid."""
    async with httpx.AsyncClient() as client:
        form_data = {
            "rfq_id": TEST_RFQ_ID,
            "supplier_id": TEST_SUPPLIER_ID,
            "supplier_name": TEST_SUPPLIER_NAME,
            "bid_price": str(bid_price)
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/auction/bid",
                data=form_data,
                headers={"Accept": "application/json"}
            )
            
            result = response.json()
            
            if result.get("success"):
                print(f"✅ Bid #{bid_number} placed successfully:")
                print(f"   Price: ${bid_price:.2f}")
                print(f"   Bid ID: {result.get('bid_id', 'N/A')}")
                print(f"   Message: {result.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ Bid #{bid_number} failed:")
                print(f"   Error: {result.get('error', result.get('errors', 'Unknown error'))}")
                return False
                
        except Exception as e:
            print(f"❌ Bid #{bid_number} failed with exception:")
            print(f"   {str(e)}")
            return False

async def test_multiple_bids():
    """Test placing multiple bids from the same supplier."""
    print("=" * 70)
    print("TESTING MULTIPLE BIDS FROM SAME SUPPLIER")
    print("=" * 70)
    print(f"\nTest Configuration:")
    print(f"  RFQ ID: {TEST_RFQ_ID}")
    print(f"  Supplier ID: {TEST_SUPPLIER_ID}")
    print(f"  Supplier Name: {TEST_SUPPLIER_NAME}")
    print(f"  Base URL: {BASE_URL}")
    print("\n" + "-" * 70)
    
    # Test bids with different prices
    test_bids = [
        3.50,  # First bid
        3.25,  # Lower bid
        3.00,  # Even lower bid
        3.10,  # Slightly higher than the lowest
        2.95   # New lowest bid
    ]
    
    print(f"\nPlacing {len(test_bids)} test bids...\n")
    
    results = []
    for i, price in enumerate(test_bids, 1):
        print(f"Placing bid #{i} at ${price:.2f}...")
        success = await place_test_bid(price, i)
        results.append(success)
        print()
        
        # Small delay between bids to ensure different timestamps
        await asyncio.sleep(0.5)
    
    # Summary
    print("-" * 70)
    print("\nTEST SUMMARY:")
    print(f"  Total bids attempted: {len(test_bids)}")
    print(f"  Successful: {sum(results)}")
    print(f"  Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✅ ALL BIDS PLACED SUCCESSFULLY!")
        print("\nNext steps:")
        print(f"  1. Visit: {BASE_URL}/auction/{TEST_RFQ_ID}")
        print(f"  2. Verify that you see {len(test_bids)} bids from '{TEST_SUPPLIER_NAME}'")
        print(f"  3. Check that each bid has a different price and timestamp")
    else:
        print("\n⚠️  SOME BIDS FAILED!")
        print("\nTroubleshooting:")
        print("  1. Make sure the backend server is running")
        print("  2. Verify the RFQ ID exists and is an active reverse auction")
        print("  3. Check that the auction hasn't ended")
        print("  4. Review server logs for error details")
    
    print("\n" + "=" * 70)

async def get_auction_status():
    """Fetch and display current auction status."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/auction/{TEST_RFQ_ID}/status")
            data = response.json()
            
            if data.get("success"):
                bids = data.get("bids", [])
                print(f"\nCurrent Auction Status:")
                print(f"  Total bids: {len(bids)}")
                
                # Count bids from our test supplier
                test_supplier_bids = [b for b in bids if b.get("supplier_id") == TEST_SUPPLIER_ID]
                print(f"  Bids from {TEST_SUPPLIER_NAME}: {len(test_supplier_bids)}")
                
                if test_supplier_bids:
                    print(f"\n  Bids from {TEST_SUPPLIER_NAME}:")
                    for i, bid in enumerate(test_supplier_bids, 1):
                        print(f"    {i}. ${bid.get('bid_price', 0):.2f} at {bid.get('timestamp', 'N/A')}")
            else:
                print(f"\n❌ Failed to fetch auction status: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"\n❌ Failed to fetch auction status: {str(e)}")

async def main():
    """Main test function."""
    print("\n🔍 Checking if server is running...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL)
            print("✅ Server is running!\n")
    except Exception as e:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print(f"   Error: {str(e)}")
        print("\n   Please start the server with: uvicorn main:app --reload")
        return
    
    # Check if RFQ ID is set
    if TEST_RFQ_ID == "YOUR_RFQ_ID_HERE":
        print("⚠️  WARNING: Please update TEST_RFQ_ID in this script with a real RFQ ID")
        print("\nTo find an RFQ ID:")
        print("  1. Visit http://localhost:8000/rfq/auctions")
        print("  2. Click on an auction")
        print("  3. Copy the RFQ ID from the URL")
        print("  4. Update TEST_RFQ_ID in this script")
        return
    
    # Run the test
    await test_multiple_bids()
    
    # Show current status
    print("\n🔍 Fetching current auction status...")
    await get_auction_status()

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("REVERSE AUCTION - MULTIPLE BIDS TEST")
    print("=" * 70)
    asyncio.run(main())
