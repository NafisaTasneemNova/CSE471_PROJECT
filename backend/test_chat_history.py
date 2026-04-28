import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["texbid_db"]
    
    rfq_id = "7985b314-a785-4aa6-a991-5102d561561f"
    receiver_id = "SUP100001"
    user_id = "34cdba7d-6ba8-402f-b59c-73ff7f4db9b1"
    company_id = None
    
    user_ids = [user_id]
    if company_id:
        user_ids.append(company_id)
        company = await db["companies"].find_one({"id": company_id})
        if company and company.get("unique_id"):
            user_ids.append(company.get("unique_id"))
            
    user_ids = list(set([uid for uid in user_ids if uid]))

    query = {"rfq_id": rfq_id}
    if receiver_id:
        query["$or"] = [
            {"sender_id": {"$in": user_ids}, "receiver_id": receiver_id},
            {"sender_id": receiver_id, "receiver_id": {"$in": user_ids}},
        ]
    
    print(f"Query: {query}")
    
    messages = []
    try:
        async for msg in db["messages"].find(query).sort("timestamp", 1).limit(200):
            msg.pop("_id", None)
            if hasattr(msg.get("timestamp"), "isoformat"):
                msg["timestamp"] = msg["timestamp"].isoformat() + "Z"
            messages.append(msg)
        print(f"Found {len(messages)} messages")
        for m in messages:
            print(m)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
