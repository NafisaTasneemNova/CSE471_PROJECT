import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["texbid_db"]
    
    bidder_ids = ["f58fe80b-979a-49ad-9dd1-1514d22bd953", "SUP100001"]
    bids_cursor = db["bids"].find({"supplier_id": {"$in": bidder_ids}}).sort("timestamp", -1)
    bids = await bids_cursor.to_list(length=100)
    print(f"Found {len(bids)} bids")
    
    rfq_ids = list(set([bid.get("rfq_id") for bid in bids if bid.get("rfq_id")]))
    rfqs_cursor = db["rfqs"].find({"id": {"$in": rfq_ids}})
    rfqs_list = await rfqs_cursor.to_list(length=len(rfq_ids))
    rfqs_map = {rfq.get("id"): rfq for rfq in rfqs_list}
    print("RFQ Map done")
    
    buyer_ids = list(set([rfq.get("buyer_id") for rfq in rfqs_list if rfq.get("buyer_id")]))
    buyers_cursor = db["users"].find({"id": {"$in": buyer_ids}})
    buyers_list = await buyers_cursor.to_list(length=len(buyer_ids))
    buyers_map = {b.get("id"): b for b in buyers_list}
    print("Buyer map done")
    
    buyer_company_ids = list(set([b.get("company_id") for b in buyers_list if b.get("company_id")]))
    buyer_companies_cursor = db["companies"].find({"id": {"$in": buyer_company_ids}})
    buyer_companies_list = await buyer_companies_cursor.to_list(length=len(buyer_company_ids))
    buyer_companies_map = {c.get("id"): c for c in buyer_companies_list}
    print("Buyer company map done")

if __name__ == "__main__":
    asyncio.run(main())
