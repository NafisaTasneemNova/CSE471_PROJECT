import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["texbid_db"]
    
    buyer = await db["users"].find_one({"email": "buyer@texbid.com"})
    if buyer:
        print(f"Buyer ID: {buyer.get('id')}")
    else:
        print("Buyer not found!")

if __name__ == "__main__":
    asyncio.run(main())
