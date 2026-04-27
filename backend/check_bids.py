import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["texbid_db"]
    bids = await db["bids"].find().to_list(length=10)
    for bid in bids:
        print(f"Bid ID: {bid.get('id', bid.get('_id'))}, Supplier ID: {bid.get('supplier_id')}, Supplier Name: {bid.get('supplier_name')}")

if __name__ == "__main__":
    asyncio.run(main())
