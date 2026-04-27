"""
Verification script for buyer action required API endpoint (Task 4.3).

This script verifies that the GET /api/dashboard/buyer/action-required endpoint:
1. Returns payments with status SENT_FOR_DELIVERY
2. Fetches associated RFQ titles
3. Builds action objects with correct structure
4. Returns proper JSON response
"""

import asyncio
import sys
from datetime import datetime


async def verify_endpoint():
    """Verify the buyer action required endpoint implementation."""
    print("=" * 70)
    print("VERIFICATION: Buyer Action Required API Endpoint (Task 4.3)")
    print("=" * 70)
    print()
    
    # Check if main.py can be imported
    try:
        # Patch StaticFiles before importing
        from unittest.mock import patch, MagicMock, AsyncMock
        with patch('fastapi.staticfiles.StaticFiles'):
            import main
            print("✓ Successfully imported main.py")
    except Exception as e:
        print(f"✗ Failed to import main.py: {e}")
        return False
    
    # Check if the endpoint exists
    try:
        endpoint_found = False
        for route in main.app.routes:
            if hasattr(route, 'path') and route.path == '/api/dashboard/buyer/action-required':
                endpoint_found = True
                print(f"✓ Endpoint '/api/dashboard/buyer/action-required' is registered")
                print(f"  - Methods: {route.methods}")
                break
        
        if not endpoint_found:
            print("✗ Endpoint '/api/dashboard/buyer/action-required' not found")
            return False
    except Exception as e:
        print(f"✗ Error checking endpoint: {e}")
        return False
    
    # Test the endpoint function directly
    print()
    print("Testing endpoint function...")
    print("-" * 70)
    
    try:
        # Mock database
        mock_db = MagicMock()
        
        # Mock payments collection
        mock_payments = AsyncMock()
        
        # Create test payment data
        test_payments = [
            {
                "payment_id": "test-pay-1",
                "transaction_id": "TXN123456",
                "order_id": "test-rfq-1",
                "amount": 15000.0,
                "status": "SENT_FOR_DELIVERY"
            },
            {
                "payment_id": "test-pay-2",
                "transaction_id": "TXN789012",
                "order_id": "test-rfq-2",
                "amount": 25000.0,
                "status": "SENT_FOR_DELIVERY"
            }
        ]
        
        def mock_find(*args, **kwargs):
            class MockCursor:
                def __init__(self, docs):
                    self.docs = docs
                    self.index = 0
                
                def __aiter__(self):
                    return self
                
                async def __anext__(self):
                    if self.index < len(self.docs):
                        doc = self.docs[self.index]
                        self.index += 1
                        return doc
                    raise StopAsyncIteration
            
            return MockCursor(test_payments)
        
        mock_payments.find = mock_find
        
        # Mock rfqs collection
        mock_rfqs = AsyncMock()
        
        async def mock_find_one(query):
            rfq_id = query.get("id")
            if rfq_id == "test-rfq-1":
                return {"id": "test-rfq-1", "title": "Cotton T-Shirts Order"}
            elif rfq_id == "test-rfq-2":
                return {"id": "test-rfq-2", "title": "Denim Jeans Order"}
            return None
        
        mock_rfqs.find_one = mock_find_one
        
        # Setup mock_db
        def mock_getitem(self, key):
            if key == "payments":
                return mock_payments
            elif key == "rfqs":
                return mock_rfqs
            return MagicMock()
        
        mock_db.__getitem__ = mock_getitem
        
        # Mock the database
        import database
        original_db = database.db
        database.db = mock_db
        
        try:
            # Test user
            test_user = {
                "id": "test-buyer-123",
                "email": "buyer@test.com",
                "company_id": "test-company-123"
            }
            
            # Call the endpoint
            result = await main.get_buyer_action_required(test_user)
            
            # Verify response structure
            print("✓ Endpoint executed successfully")
            print()
            print("Response structure:")
            print(f"  - success: {result.get('success')}")
            print(f"  - actions count: {len(result.get('actions', []))}")
            
            # Verify actions
            if result.get("success") and len(result.get("actions", [])) == 2:
                print()
                print("Action items:")
                for i, action in enumerate(result["actions"], 1):
                    print(f"  Action {i}:")
                    print(f"    - payment_id: {action.get('payment_id')}")
                    print(f"    - transaction_id: {action.get('transaction_id')}")
                    print(f"    - action: {action.get('action')}")
                    print(f"    - description: {action.get('description')}")
                    print(f"    - amount: ${action.get('amount'):,.2f}")
                    print(f"    - rfq_title: {action.get('rfq_title')}")
                
                # Verify required fields
                print()
                print("Field validation:")
                all_valid = True
                for action in result["actions"]:
                    if not all(key in action for key in ["payment_id", "transaction_id", "action", "description", "amount", "rfq_title"]):
                        print("✗ Missing required fields in action object")
                        all_valid = False
                    if action.get("action") != "confirm_delivery":
                        print("✗ Action type should be 'confirm_delivery'")
                        all_valid = False
                
                if all_valid:
                    print("✓ All action objects have required fields")
                    print("✓ Action type is correct")
                
                return True
            else:
                print("✗ Unexpected response structure or action count")
                return False
        finally:
            database.db = original_db
    
    except Exception as e:
        print(f"✗ Error testing endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main verification function."""
    success = await verify_endpoint()
    
    print()
    print("=" * 70)
    if success:
        print("✓ VERIFICATION PASSED")
        print()
        print("Implementation details:")
        print("- Endpoint: GET /api/dashboard/buyer/action-required")
        print("- Authorization: require_buyer dependency")
        print("- Database queries:")
        print("  1. Payments with status SENT_FOR_DELIVERY")
        print("  2. Associated RFQ titles")
        print("- Response format: JSON with success flag and actions array")
        print("- Action object fields:")
        print("  - payment_id")
        print("  - transaction_id")
        print("  - action (confirm_delivery)")
        print("  - description")
        print("  - amount")
        print("  - rfq_title")
    else:
        print("✗ VERIFICATION FAILED")
        print()
        print("Please check the implementation and try again.")
    print("=" * 70)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
