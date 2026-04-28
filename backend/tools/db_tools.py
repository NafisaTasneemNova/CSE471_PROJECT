"""
TexBid Database Tools
=====================
A single utility script combining all database maintenance tasks.

Usage:
    python tools/db_tools.py

Then choose an option from the menu.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "texbid_db"


def get_db():
    client = AsyncIOMotorClient(MONGO_URL)
    return client, client[DB_NAME]


# ─── ADMIN TOOLS ────────────────────────────────────────────────────────────

async def make_admin():
    """Grant admin access to a user by email."""
    client, db = get_db()
    email = input("Enter email to grant admin: ").strip()
    user = await db["users"].find_one({"email": email})
    if not user:
        print(f"❌ User not found: {email}. Register first at /register")
    else:
        result = await db["users"].update_one({"email": email}, {"$set": {"is_admin": True}})
        if result.modified_count > 0:
            print(f"✅ {email} is now an admin. Login at http://localhost:8000/admin/login")
        else:
            print(f"ℹ️  {email} was already an admin.")
    client.close()


async def remove_admin():
    """Revoke admin access from a user by email."""
    client, db = get_db()
    email = input("Enter email to revoke admin: ").strip()
    result = await db["users"].update_one({"email": email}, {"$set": {"is_admin": False}})
    print(f"✅ Admin access removed for {email}" if result.modified_count else f"ℹ️  No change for {email}")
    client.close()


# ─── SUBSCRIPTION TOOLS ─────────────────────────────────────────────────────

async def reset_subscription_locks():
    """Reset all subscription locks so users can freely change their plan."""
    client, db = get_db()
    result = await db["companies"].update_many(
        {},
        {"$set": {"subscription_start_date": None, "subscription_can_change_after": None}}
    )
    print(f"✅ Reset subscription locks for {result.modified_count} companies.")
    client.close()


async def set_all_free():
    """Downgrade all companies to FREE plan."""
    client, db = get_db()
    confirm = input("⚠️  This will set ALL companies to FREE. Type 'yes' to confirm: ")
    if confirm.lower() == "yes":
        result = await db["companies"].update_many({}, {"$set": {"subscription_tier": "FREE"}})
        print(f"✅ Set {result.modified_count} companies to FREE.")
    else:
        print("Cancelled.")
    client.close()


# ─── BID TOOLS ──────────────────────────────────────────────────────────────

async def list_bids():
    """List all bids in the database."""
    client, db = get_db()
    bids = await db["bids"].find({}).to_list(length=100)
    print(f"\n📊 Total bids: {len(bids)}\n")
    for i, bid in enumerate(bids, 1):
        print(f"{i}. ID={bid.get('id','N/A')} | Supplier={bid.get('supplier_name','N/A')} "
              f"| RFQ={bid.get('rfq_id','N/A')} | Price={bid.get('bid_price',0)} "
              f"| Status={bid.get('status','N/A')}")
    client.close()


async def remove_buyer_bids():
    """Remove bids accidentally placed by buyer companies."""
    client, db = get_db()
    name = input("Enter buyer company name to remove bids for: ").strip()
    result = await db["bids"].delete_many({"supplier_name": name})
    print(f"✅ Deleted {result.deleted_count} bids from '{name}'.")
    remaining = await db["bids"].count_documents({})
    print(f"📊 Total remaining bids: {remaining}")
    client.close()


# ─── COMPANY / USER TOOLS ───────────────────────────────────────────────────

async def list_companies():
    """List all companies with their roles and subscription tiers."""
    client, db = get_db()
    print("\n📋 Companies:\n")
    async for comp in db["companies"].find():
        print(f"  {comp.get('name','?'):30} | Role={comp.get('role','?'):10} "
              f"| Tier={comp.get('subscription_tier','FREE'):10} "
              f"| ID={comp.get('unique_id') or comp.get('id','?')}")
    client.close()


async def delete_duplicate_company():
    """Delete a company by its internal MongoDB id (for fixing duplicates)."""
    client, db = get_db()
    company_id = input("Enter the company 'id' field to delete: ").strip()
    result = await db["companies"].delete_one({"id": company_id})
    print(f"✅ Deleted {result.deleted_count} company with id={company_id}")
    client.close()


# ─── MENU ────────────────────────────────────────────────────────────────────

MENU = {
    "1": ("Make user admin",              make_admin),
    "2": ("Remove admin access",          remove_admin),
    "3": ("Reset subscription locks",     reset_subscription_locks),
    "4": ("Set all companies to FREE",    set_all_free),
    "5": ("List all bids",                list_bids),
    "6": ("Remove buyer bids",            remove_buyer_bids),
    "7": ("List all companies",           list_companies),
    "8": ("Delete duplicate company",     delete_duplicate_company),
}


async def main():
    print("\n╔══════════════════════════════╗")
    print("║   TexBid DB Tools            ║")
    print("╚══════════════════════════════╝\n")
    for key, (label, _) in MENU.items():
        print(f"  {key}. {label}")
    print()
    choice = input("Choose an option: ").strip()
    if choice in MENU:
        await MENU[choice][1]()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    asyncio.run(main())
