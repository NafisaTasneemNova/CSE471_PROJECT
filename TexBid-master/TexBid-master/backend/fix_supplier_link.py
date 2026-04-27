"""
Fix script: links the supplier user to the correct SUPPLIER company.
Run once: python fix_supplier_link.py
"""
import asyncio
import random
import string
from motor.motor_asyncio import AsyncIOMotorClient


async def fix():
    c = AsyncIOMotorClient("mongodb://localhost:27017")
    db = c["texbid_db"]

    # Show current state
    print("=== Current State ===")
    users = await db["users"].find({}).to_list(50)
    for u in users:
        co = await db["companies"].find_one({"id": u.get("company_id")})
        role = co.get("role") if co else "NO COMPANY"
        print(f"  User: {u.get('email')} → company role: {role} | company_id: {u.get('company_id')}")

    print("\n=== Companies ===")
    companies = await db["companies"].find({}).to_list(50)
    for co in companies:
        print(f"  {co.get('id')} | {co.get('name')} | {co.get('role')} | unique_id: {co.get('unique_id')}")

    # Fix each user that is linked to a BUYER company but whose email suggests supplier
    # More broadly: fix any SUPPLIER company that has no linked user
    for co in companies:
        if co.get("role") == "SUPPLIER":
            # Check if any user points to this company
            linked_user = await db["users"].find_one({"company_id": co.get("id")})
            if not linked_user:
                print(f"\nSUPPLIER company '{co.get('name')}' has no linked user.")
                # Find a user with same name pattern or ask
                # For now: find users whose email contains 'sup' or who have a BUYER company with same name
                buyer_co = await db["companies"].find_one({
                    "name": co.get("name"),
                    "role": "BUYER"
                })
                if buyer_co:
                    user = await db["users"].find_one({"company_id": buyer_co.get("id")})
                    if user:
                        print(f"  Found user {user.get('email')} linked to BUYER version of same company.")
                        print(f"  Relinking to SUPPLIER company...")

                        # Ensure supplier company has a unique_id
                        if not co.get("unique_id"):
                            uid = "SUP" + "".join(random.choices(string.digits, k=6))
                            while await db["companies"].find_one({"unique_id": uid}):
                                uid = "SUP" + "".join(random.choices(string.digits, k=6))
                            await db["companies"].update_one(
                                {"id": co.get("id")},
                                {"$set": {"unique_id": uid}}
                            )
                            print(f"  Assigned unique_id={uid} to SUPPLIER company")

                        # Relink user to SUPPLIER company
                        await db["users"].update_one(
                            {"id": user.get("id")},
                            {"$set": {"company_id": co.get("id")}}
                        )
                        print(f"  ✅ User {user.get('email')} now linked to SUPPLIER company")

    print("\n=== Fixed State ===")
    users = await db["users"].find({}).to_list(50)
    for u in users:
        co = await db["companies"].find_one({"id": u.get("company_id")})
        role = co.get("role") if co else "NO COMPANY"
        uid = co.get("unique_id") if co else "—"
        print(f"  User: {u.get('email')} → role: {role} | unique_id: {uid}")

    c.close()


asyncio.run(fix())
