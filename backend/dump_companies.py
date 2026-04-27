import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["texbid_db"]
    print("Companies:")
    async for comp in db["companies"].find():
        print(f"ID: {comp.get('id')}, Unique ID: {comp.get('unique_id')}, Name: {comp.get('name')}, Role: {comp.get('role')}")

    print("\nUsers:")
    async for user in db["users"].find({"email": "seller@texbid"}):
        print(f"ID: {user.get('id')}, Email: {user.get('email')}, Company ID: {user.get('company_id')}")

if __name__ == "__main__":
    asyncio.run(main())
