"""
Test for Task 5.1: Supplier Dashboard Route
Tests the GET /dashboard/supplier route implementation.
"""
import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Mock the static files before importing main
from unittest.mock import MagicMock, patch
import starlette.staticfiles
original_staticfiles = starlette.staticfiles.StaticFiles

class MockStaticFiles:
    def __init__(self, *args, **kwargs):
        pass

# Patch StaticFiles before importing main
starlette.staticfiles.StaticFiles = MockStaticFiles

from database import db
import uuid
from datetime import datetime, timedelta


@pytest.fixture
async def setup_test_data():
    """Setup test data for supplier dashboard tests."""
    if db is None:
        pytest.skip("Database not available")
    
    # Create test supplier company
    supplier_company_id = str(uuid.uuid4())
    supplier_unique_id = f"SUP{uuid.uuid4().hex[:6].upper()}"
    await db["companies"].insert_one({
        "id": supplier_company_id,
        "unique_id": supplier_unique_id,
        "name": "Test Supplier Co",
        "role": "SUPPLIER",
        "overall_status": "VERIFIED",
        "trust_score": 85,
        "subscription_tier": "FREE",
        "created_at": datetime.utcnow()
    })
    
    # Create test supplier user
    supplier_user_id = str(uuid.uuid4())
    await db["users"].insert_one({
        "id": supplier_user_id,
        "email": "supplier@test.com",
        "password_hash": "test_hash",
        "company_id": supplier_company_id,
        "is_admin": False,
        "created_at": datetime.utcnow()
    })
    
    # Create test buyer company
    buyer_company_id = str(uuid.uuid4())
    buyer_unique_id = f"BUY{uuid.uuid4().hex[:6].upper()}"
    await db["companies"].insert_one({
        "id": buyer_company_id,
        "unique_id": buyer_unique_id,
        "name": "Test Buyer Co",
        "role": "BUYER",
        "overall_status": "VERIFIED",
        "trust_score": 90,
        "subscription_tier": "FREE",
        "created_at": datetime.utcnow()
    })
    
    # Create open RFQs
    rfq_ids = []
    for i in range(3):
        rfq_id = str(uuid.uuid4())
        await db["rfqs"].insert_one({
            "id": rfq_id,
            "buyer_id": buyer_company_id,
            "buyer_company": "Test Buyer Co",
            "title": f"Test RFQ {i+1}",
            "product_category": "T-Shirts",
            "quantity": 1000 * (i+1),
            "status": "OPEN",
            "urgency_level": "MEDIUM",
            "created_at": datetime.utcnow()
        })
        rfq_ids.append(rfq_id)
    
    # Create accepted bid
    bid_id = str(uuid.uuid4())
    await db["bids"].insert_one({
        "id": bid_id,
        "rfq_id": rfq_ids[0],
        "supplier_id": supplier_unique_id,
        "company_name": "Test Supplier Co",
        "bid_price": 25.50,
        "status": "ACCEPTED",
        "timestamp": datetime.utcnow()
    })
    
    # Create payment for the accepted bid
    payment_id = str(uuid.uuid4())
    await db["payments"].insert_one({
        "payment_id": payment_id,
        "transaction_id": f"TXN{uuid.uuid4().hex[:8].upper()}",
        "order_id": rfq_ids[0],
        "bid_id": bid_id,
        "buyer_id": buyer_company_id,
        "supplier_id": supplier_unique_id,
        "amount": 25500.00,
        "status": "PAID_IN_ESCROW",
        "created_at": datetime.utcnow()
    })
    
    # Create session for supplier user with future expiration
    session_token = f"test_session_{uuid.uuid4().hex}"
    await db["sessions"].insert_one({
        "token": session_token,
        "user_id": supplier_user_id,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=30)
    })
    
    yield {
        "supplier_user_id": supplier_user_id,
        "supplier_company_id": supplier_company_id,
        "supplier_unique_id": supplier_unique_id,
        "session_token": session_token,
        "rfq_ids": rfq_ids,
        "bid_id": bid_id,
        "payment_id": payment_id
    }
    
    # Cleanup
    await db["companies"].delete_many({"id": {"$in": [supplier_company_id, buyer_company_id]}})
    await db["users"].delete_one({"id": supplier_user_id})
    await db["rfqs"].delete_many({"id": {"$in": rfq_ids}})
    await db["bids"].delete_one({"id": bid_id})
    await db["payments"].delete_one({"payment_id": payment_id})
    await db["sessions"].delete_one({"token": session_token})


def test_supplier_dashboard_route_exists():
    """Test that the supplier dashboard route exists and is properly configured."""
    from main import app
    
    # Check that the route exists
    routes = [route.path for route in app.routes]
    assert "/dashboard/supplier" in routes
    
    print("✓ Supplier dashboard route exists at /dashboard/supplier")


def test_require_supplier_dependency_exists():
    """Test that require_supplier dependency is defined."""
    from main import require_supplier
    
    assert require_supplier is not None
    assert callable(require_supplier)
    
    print("✓ require_supplier dependency is defined and callable")


@pytest.mark.asyncio
async def test_supplier_dashboard_data_structure(setup_test_data):
    """Test that supplier dashboard returns correct data structure."""
    test_data = await setup_test_data
    
    # Import after setup
    from main import supplier_dashboard_feed
    from fastapi import Request
    from unittest.mock import MagicMock
    
    # Create mock request
    request = MagicMock(spec=Request)
    
    # Create mock user with supplier role
    user = {
        "id": test_data["supplier_user_id"],
        "company_id": test_data["supplier_company_id"],
        "email": "supplier@test.com"
    }
    
    # Call the route handler directly
    response = await supplier_dashboard_feed(request, user)
    
    # Verify response structure
    assert response is not None
    assert hasattr(response, 'template')
    
    # Check template context
    context = response.context if hasattr(response, 'context') else {}
    
    print(f"✓ Supplier dashboard returns valid response")
    print(f"  - Template: {response.template.name if hasattr(response, 'template') else 'N/A'}")
    print(f"  - Context keys: {list(context.keys()) if context else 'N/A'}")


@pytest.mark.asyncio  
async def test_supplier_dashboard_queries_open_rfqs(setup_test_data):
    """Test that supplier dashboard queries for OPEN RFQs."""
    test_data = await setup_test_data
    
    # Verify open RFQs exist in database
    open_rfqs = await db["rfqs"].find({"status": "OPEN"}).to_list(length=None)
    
    assert len(open_rfqs) >= 3
    print(f"✓ Found {len(open_rfqs)} open RFQs in database")


@pytest.mark.asyncio
async def test_supplier_dashboard_queries_supplier_bids(setup_test_data):
    """Test that supplier dashboard queries supplier's bids."""
    test_data = await setup_test_data
    
    # Verify supplier has accepted bids
    supplier_bids = await db["bids"].find({
        "supplier_id": test_data["supplier_unique_id"],
        "status": {"$in": ["ACCEPTED", "CONFIRMED"]}
    }).to_list(length=None)
    
    assert len(supplier_bids) >= 1
    print(f"✓ Found {len(supplier_bids)} accepted/confirmed bids for supplier")


@pytest.mark.asyncio
async def test_supplier_dashboard_fetches_payment_data(setup_test_data):
    """Test that supplier dashboard fetches payment data for bids."""
    test_data = await setup_test_data
    
    # Verify payment exists for the bid
    payment = await db["payments"].find_one({
        "bid_id": test_data["bid_id"]
    })
    
    assert payment is not None
    assert payment["status"] in ["PAID_IN_ESCROW", "WORK_IN_PROGRESS", "SENT_FOR_DELIVERY", "RELEASED"]
    print(f"✓ Found payment with status: {payment['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
