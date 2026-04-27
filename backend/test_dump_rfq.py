import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["texbid_db"]
    
    rfq = await db["rfqs"].find_one({"id": "7985b314-a785-4aa6-a991-5102d561561f"})
    if rfq:
        print(f"RFQ Buyer ID: {rfq.get('buyer_id')}")

if __name__ == "__main__":
    asyncio.run(main())
