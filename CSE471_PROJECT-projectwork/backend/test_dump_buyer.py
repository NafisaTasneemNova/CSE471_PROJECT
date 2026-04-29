import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["texbid_db"]
    
    buyer = await db["users"].find_one({"email": "buyer@texbid.com"})
    print(buyer)
    company = await db["companies"].find_one({"id": buyer.get("company_id")})
    print(company)

if __name__ == "__main__":
    asyncio.run(main())
