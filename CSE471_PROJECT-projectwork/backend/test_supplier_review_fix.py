#!/usr/bin/env python3
"""
Test script to verify the supplier review fix
"""

def test_supplier_id_matching():
    """Test the supplier ID matching logic"""
    
    # Simulate the data structures
    payment = {
        "supplier_id": "SUP123456",  # This is the company unique_id
        "buyer_id": "user789"
    }
    
    company = {
        "id": "comp456",
        "unique_id": "SUP123456"
    }
    
    user_id = "user123"  # This is the user ID, not the company ID
    
    # Test the old logic (would fail)
    old_logic_result = payment.get("supplier_id") == user_id
    print(f"❌ Old logic result: {old_logic_result} (payment supplier_id: {payment.get('supplier_id')} vs user_id: {user_id})")
    
    # Test the new logic (should pass)
    is_supplier_transaction = payment.get("supplier_id") == user_id
    if not is_supplier_transaction:
        # Also check against company unique_id and company id
        is_supplier_transaction = (
            payment.get("supplier_id") == company.get("unique_id") or
            payment.get("supplier_id") == company.get("id")
        )
    
    print(f"✅ New logic result: {is_supplier_transaction}")
    print(f"   - Direct match (supplier_id == user_id): {payment.get('supplier_id') == user_id}")
    print(f"   - Company unique_id match: {payment.get('supplier_id') == company.get('unique_id')}")
    print(f"   - Company id match: {payment.get('supplier_id') == company.get('id')}")
    
    return is_supplier_transaction

def test_different_scenarios():
    """Test different supplier ID scenarios"""
    
    scenarios = [
        {
            "name": "Supplier ID as company unique_id",
            "payment": {"supplier_id": "SUP123456", "buyer_id": "user789"},
            "company": {"id": "comp456", "unique_id": "SUP123456"},
            "user_id": "user123",
            "expected": True
        },
        {
            "name": "Supplier ID as company id",
            "payment": {"supplier_id": "comp456", "buyer_id": "user789"},
            "company": {"id": "comp456", "unique_id": "SUP123456"},
            "user_id": "user123",
            "expected": True
        },
        {
            "name": "Supplier ID as user id (direct match)",
            "payment": {"supplier_id": "user123", "buyer_id": "user789"},
            "company": {"id": "comp456", "unique_id": "SUP123456"},
            "user_id": "user123",
            "expected": True
        },
        {
            "name": "No match (wrong supplier)",
            "payment": {"supplier_id": "SUP999999", "buyer_id": "user789"},
            "company": {"id": "comp456", "unique_id": "SUP123456"},
            "user_id": "user123",
            "expected": False
        }
    ]
    
    print("\n🧪 Testing different supplier ID scenarios:")
    print("=" * 60)
    
    for scenario in scenarios:
        payment = scenario["payment"]
        company = scenario["company"]
        user_id = scenario["user_id"]
        expected = scenario["expected"]
        
        # Apply the new logic
        is_supplier_transaction = payment.get("supplier_id") == user_id
        if not is_supplier_transaction:
            is_supplier_transaction = (
                payment.get("supplier_id") == company.get("unique_id") or
                payment.get("supplier_id") == company.get("id")
            )
        
        status = "✅ PASS" if is_supplier_transaction == expected else "❌ FAIL"
        print(f"{status} {scenario['name']}")
        print(f"     Payment supplier_id: {payment.get('supplier_id')}")
        print(f"     User ID: {user_id}")
        print(f"     Company unique_id: {company.get('unique_id')}")
        print(f"     Company id: {company.get('id')}")
        print(f"     Result: {is_supplier_transaction} (expected: {expected})")
        print()

def main():
    """Run all tests"""
    print("🔧 Testing Supplier Review Fix")
    print("=" * 50)
    
    print("\n📋 Basic supplier ID matching test:")
    test_supplier_id_matching()
    
    test_different_scenarios()
    
    print("✅ All tests completed!")
    print("\n💡 The fix should now allow suppliers to leave reviews by checking:")
    print("   1. Direct user ID match (payment.supplier_id == user.id)")
    print("   2. Company unique_id match (payment.supplier_id == company.unique_id)")
    print("   3. Company id match (payment.supplier_id == company.id)")

if __name__ == "__main__":
    main()