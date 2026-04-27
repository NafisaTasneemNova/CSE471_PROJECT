"""Seed demo supplier bids for testing the Bid Comparison Matrix."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid


async def seed_demo():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["texbid_db"]

    # Find the most recent RFQ
    rfqs = await db["rfqs"].find({}).sort("created_at", -1).to_list(length=5)
    if not rfqs:
        print("No RFQs found. Please create one first.")
        return

    rfq = rfqs[0]
    rfq_id = rfq["id"]
    print(f"Using RFQ: {rfq.get('title', 'Untitled')} (ID: {rfq_id})")

    # Create 4 supplier companies
    suppliers = [
        {
            "id": str(uuid.uuid4()), "unique_id": "SUP100001",
            "name": "Shanghai Silk Co.", "role": "SUPPLIER",
            "overall_status": "VERIFIED", "trust_score": 92,
            "subscription_tier": "PREMIUM", "created_at": datetime.utcnow(),
        },
        {
            "id": str(uuid.uuid4()), "unique_id": "SUP200002",
            "name": "Dhaka Garments Ltd", "role": "SUPPLIER",
            "overall_status": "VERIFIED", "trust_score": 78,
            "subscription_tier": "FREE", "created_at": datetime.utcnow(),
        },
        {
            "id": str(uuid.uuid4()), "unique_id": "SUP300003",
            "name": "Istanbul Textiles", "role": "SUPPLIER",
            "overall_status": "VERIFIED", "trust_score": 85,
            "subscription_tier": "PREMIUM", "created_at": datetime.utcnow(),
        },
        {
            "id": str(uuid.uuid4()), "unique_id": "SUP400004",
            "name": "Vietnam Fabric Corp", "role": "SUPPLIER",
            "overall_status": "PENDING_REVIEW", "trust_score": 65,
            "subscription_tier": "FREE", "created_at": datetime.utcnow(),
        },
    ]

    for s in suppliers:
        existing = await db["companies"].find_one({"unique_id": s["unique_id"]})
        if not existing:
            await db["companies"].insert_one(s)
            print(f"  Created supplier: {s['name']}")
        else:
            print(f"  Supplier exists: {s['name']}")

    # Create bids
    bids = [
        {
            "id": str(uuid.uuid4()), "rfq_id": rfq_id,
            "supplier_id": "SUP100001", "supplier_name": "Shanghai Silk Co.",
            "bid_price": 4.25, "timestamp": datetime.utcnow(),
            "status": "ACTIVE", "delivery_time_days": 28, "incoterms": "FOB",
            "quality_notes": "ISO 9001 certified. Premium 100% combed cotton, 180 GSM ringspun. Pre-shrunk guarantee.",
            "bid_status": "PENDING",
        },
        {
            "id": str(uuid.uuid4()), "rfq_id": rfq_id,
            "supplier_id": "SUP200002", "supplier_name": "Dhaka Garments Ltd",
            "bid_price": 3.10, "timestamp": datetime.utcnow(),
            "status": "ACTIVE", "delivery_time_days": 21, "incoterms": "CIF",
            "quality_notes": "BSCI compliant. Standard cotton 160 GSM. Bulk discount available for 10k+ units.",
            "bid_status": "PENDING",
        },
        {
            "id": str(uuid.uuid4()), "rfq_id": rfq_id,
            "supplier_id": "SUP300003", "supplier_name": "Istanbul Textiles",
            "bid_price": 5.50, "timestamp": datetime.utcnow(),
            "status": "ACTIVE", "delivery_time_days": 18, "incoterms": "DDP",
            "quality_notes": "OEKO-TEX 100 certified. Organic cotton option. European quality standards.",
            "bid_status": "PENDING",
        },
        {
            "id": str(uuid.uuid4()), "rfq_id": rfq_id,
            "supplier_id": "SUP400004", "supplier_name": "Vietnam Fabric Corp",
            "bid_price": 3.75, "timestamp": datetime.utcnow(),
            "status": "ACTIVE", "delivery_time_days": 25, "incoterms": "FOB",
            "quality_notes": "WRAP certified. Cotton-polyester blend available. Fast turnaround.",
            "bid_status": "PENDING",
        },
    ]

    # Clear old demo bids for this RFQ
    deleted = await db["bids"].delete_many({"rfq_id": rfq_id})
    print(f"  Cleared {deleted.deleted_count} old bids")

    for b in bids:
        await db["bids"].insert_one(b)
        print(f"  Created bid: {b['supplier_name']} @ ${b['bid_price']}")

    print(f"\nDone! View at: http://localhost:8000/rfq/{rfq_id}/bids")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_demo())
