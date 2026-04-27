import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["texbid_db"]
    # Delete the duplicate Shanghai Silk Co. with SUP100001
    res = await db["companies"].delete_one({"id": "901e03b2-f224-4885-bb0a-96fe4239656d"})
    print(f"Deleted {res.deleted_count} duplicate company.")

if __name__ == "__main__":
    asyncio.run(main())
