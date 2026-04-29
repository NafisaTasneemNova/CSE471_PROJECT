import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["texbid_db"]
    
    # Dump messages
    print("Messages:")
    async for msg in db["messages"].find().limit(20):
        print(msg)
        
if __name__ == "__main__":
    asyncio.run(main())
