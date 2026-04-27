"""
Test for buyer recent RFQs API endpoint (Task 4.2)
"""
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.asyncio
async def test_buyer_recent_rfqs_success():
    """Test successful retrieval of buyer's recent RFQs with enriched data."""
    # Import inside test to avoid static files issue
    with patch('main.StaticFiles'):
        from main import get_buyer_recent_rfqs
    
    # Mock database
    mock_db = MagicMock()
    
    # Mock companies collection
    mock_companies = AsyncMock()
    mock_companies.find_one = AsyncMock(return_value={
        "id": "company-123",
        "unique_id": "BUY123456",
        "role": "BUYER",
        "name": "Test Buyer Company"
    })
    
    # Mock RFQ documents
    mock_rfq_docs = [
        {
            "id": "rfq-1",
            "buyer_id": "company-123",
            "title": "Cotton T-Shirts Order",
            "product_category": "T-Shirts",
            "quantity": 5000,
            "status": "OPEN",
            "created_at": datetime(2024, 1, 15, 10, 30, 0),
            "urgency_level": "HIGH",
            "fabric_type": "Cotton"
        },
        {
            "id": "rfq-2",
            "buyer_id": "company-123",
            "title": "Denim Jeans Order",
            "product_category": "Denim",
            "quantity": 3000,
            "status": "EVALUATING",
            "created_at": datetime(2024, 1, 14, 9, 0, 0),
            "urgency_level": "MEDIUM",
            "fabric_type": "Denim"
        },
        {
            "id": "rfq-3",
            "buyer_id": "company-123",
            "title": "Activewear Order",
            "product_category": "Activewear",
            "quantity": 2000,
            "status": "AWARDED",
            "created_at": datetime(2024, 1, 13, 14, 0, 0),
            "urgency_level": "LOW",
            "fabric_type": "Polyester"
        }
    ]
    
    # Mock rfqs collection
    mock_rfqs = AsyncMock()
    
    class MockRFQCursor:
        def __init__(self, docs, limit_val):
            self.docs = docs[:limit_val]
            self.index = 0
        
        def sort(self, field, direction):
            return self
        
        def limit(self, limit_val):
            self.docs = self.docs[:limit_val]
            return self
        
        def __aiter__(self):
            return self
        
        async def __anext__(self):
            if self.index < len(self.docs):
                doc = self.docs[self.index]
                self.index += 1
                return doc
            raise StopAsyncIteration
    
    def mock_find(*args, **kwargs):
        return MockRFQCursor(mock_rfq_docs, 10)
    
    mock_rfqs.find = mock_find
    
    # Mock bids collection
    mock_bids = AsyncMock()
    
    async def mock_count_documents(query):
        rfq_id = query.get("rfq_id")
        if rfq_id == "rfq-1":
            return 7
        elif rfq_id == "rfq-2":
            return 3
        elif rfq_id == "rfq-3":
            return 5
        return 0
    
    mock_bids.count_documents = mock_count_documents
    
    # Mock payments collection
    mock_payments = AsyncMock()
    
    async def mock_find_one(query):
        order_id = query.get("order_id")
        if order_id == "rfq-2":
            return {
                "payment_id": "pay-123",
                "transaction_id": "TXN123456",
                "order_id": "rfq-2",
                "amount": 15000.0,
                "status": "PAID_IN_ESCROW"
            }
        return None
    
    mock_payments.find_one = mock_find_one
    
    # Setup mock_db to return appropriate collections
    def mock_getitem(key):
        if key == "companies":
            return mock_companies
        elif key == "rfqs":
            return mock_rfqs
        elif key == "bids":
            return mock_bids
        elif key == "payments":
            return mock_payments
        return MagicMock()
    
    mock_db.__getitem__ = mock_getitem
    
    # Mock the database import
    import database
    original_db = database.db
    database.db = mock_db
    
    try:
        # Test user
        user = {
            "id": "user-123",
            "email": "buyer@test.com",
            "company_id": "company-123"
        }
        
        # Call the endpoint
        result = await get_buyer_recent_rfqs(limit=10, user=user)
        
        # Verify response structure
        assert result["success"] is True
        assert "rfqs" in result
        assert len(result["rfqs"]) == 3
        
        # Verify first RFQ has bid count
        rfq1 = result["rfqs"][0]
        assert rfq1["id"] == "rfq-1"
        assert rfq1["bid_count"] == 7
        assert rfq1["payment_status"] is None
        assert rfq1["payment_id"] is None
        
        # Verify second RFQ has payment info
        rfq2 = result["rfqs"][1]
        assert rfq2["id"] == "rfq-2"
        assert rfq2["bid_count"] == 3
        assert rfq2["payment_status"] == "PAID_IN_ESCROW"
        assert rfq2["payment_id"] == "pay-123"
        
        # Verify third RFQ
        rfq3 = result["rfqs"][2]
        assert rfq3["id"] == "rfq-3"
        assert rfq3["bid_count"] == 5
        assert rfq3["payment_status"] is None
        assert rfq3["payment_id"] is None
    finally:
        database.db = original_db


@pytest.mark.asyncio
async def test_buyer_recent_rfqs_with_limit():
    """Test limit parameter works correctly."""
    with patch('main.StaticFiles'):
        from main import get_buyer_recent_rfqs
    
    # Mock database
    mock_db = MagicMock()
    
    # Mock companies collection
    mock_companies = AsyncMock()
    mock_companies.find_one = AsyncMock(return_value={
        "id": "company-123",
        "unique_id": "BUY123456",
        "role": "BUYER",
        "name": "Test Buyer Company"
    })
    
    # Mock RFQ documents (5 RFQs)
    mock_rfq_docs = [
        {"id": f"rfq-{i}", "buyer_id": "company-123", "title": f"RFQ {i}", 
         "product_category": "T-Shirts", "quantity": 1000, "status": "OPEN",
         "created_at": datetime(2024, 1, i+1, 10, 0, 0), "urgency_level": "MEDIUM",
         "fabric_type": "Cotton"}
        for i in range(5)
    ]
    
    # Mock rfqs collection
    mock_rfqs = AsyncMock()
    
    class MockRFQCursor:
        def __init__(self, docs, limit_val):
            self.docs = docs
            self.limit_val = limit_val
            self.index = 0
        
        def sort(self, field, direction):
            return self
        
        def limit(self, limit_val):
            self.limit_val = limit_val
            return self
        
        def __aiter__(self):
            return self
        
        async def __anext__(self):
            if self.index < min(len(self.docs), self.limit_val):
                doc = self.docs[self.index]
                self.index += 1
                return doc
            raise StopAsyncIteration
    
    def mock_find(*args, **kwargs):
        return MockRFQCursor(mock_rfq_docs, 10)
    
    mock_rfqs.find = mock_find
    
    # Mock bids and payments
    mock_bids = AsyncMock()
    mock_bids.count_documents = AsyncMock(return_value=0)
    mock_payments = AsyncMock()
    mock_payments.find_one = AsyncMock(return_value=None)
    
    # Setup mock_db
    def mock_getitem(key):
        if key == "companies":
            return mock_companies
        elif key == "rfqs":
            return mock_rfqs
        elif key == "bids":
            return mock_bids
        elif key == "payments":
            return mock_payments
        return MagicMock()
    
    mock_db.__getitem__ = mock_getitem
    
    # Mock the database import
    import database
    original_db = database.db
    database.db = mock_db
    
    try:
        user = {
            "id": "user-123",
            "email": "buyer@test.com",
            "company_id": "company-123"
        }
        
        # Call with limit=2
        result = await get_buyer_recent_rfqs(limit=2, user=user)
        
        # Verify only 2 RFQs returned
        assert result["success"] is True
        assert len(result["rfqs"]) == 2
    finally:
        database.db = original_db


@pytest.mark.asyncio
async def test_buyer_recent_rfqs_database_unavailable():
    """Test endpoint returns 500 when database is unavailable."""
    with patch('main.StaticFiles'):
        from main import get_buyer_recent_rfqs
    
    # Mock database as None
    import database
    original_db = database.db
    database.db = None
    
    try:
        user = {
            "id": "user-123",
            "email": "buyer@test.com",
            "company_id": "company-123"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await get_buyer_recent_rfqs(limit=10, user=user)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Database not available"
    finally:
        database.db = original_db


@pytest.mark.asyncio
async def test_buyer_recent_rfqs_company_not_found():
    """Test endpoint returns 404 when company not found."""
    with patch('main.StaticFiles'):
        from main import get_buyer_recent_rfqs
    
    # Mock database
    mock_db = MagicMock()
    mock_companies = AsyncMock()
    mock_companies.find_one = AsyncMock(return_value=None)
    
    mock_db.__getitem__ = MagicMock(return_value=mock_companies)
    
    # Mock the database import
    import database
    original_db = database.db
    database.db = mock_db
    
    try:
        user = {
            "id": "user-999",
            "email": "buyer@test.com",
            "company_id": "nonexistent-company"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await get_buyer_recent_rfqs(limit=10, user=user)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Company not found"
    finally:
        database.db = original_db


@pytest.mark.asyncio
async def test_buyer_recent_rfqs_empty_data():
    """Test endpoint with no RFQs."""
    with patch('main.StaticFiles'):
        from main import get_buyer_recent_rfqs
    
    # Mock database
    mock_db = MagicMock()
    
    # Mock companies collection
    mock_companies = AsyncMock()
    mock_companies.find_one = AsyncMock(return_value={
        "id": "company-123",
        "unique_id": "BUY123456",
        "role": "BUYER",
        "name": "Test Buyer Company"
    })
    
    # Mock rfqs collection - no RFQs
    mock_rfqs = AsyncMock()
    
    class MockEmptyCursor:
        def sort(self, field, direction):
            return self
        
        def limit(self, limit_val):
            return self
        
        def __aiter__(self):
            return self
        
        async def __anext__(self):
            raise StopAsyncIteration
    
    mock_rfqs.find = MagicMock(return_value=MockEmptyCursor())
    
    # Setup mock_db
    def mock_getitem(key):
        if key == "companies":
            return mock_companies
        elif key == "rfqs":
            return mock_rfqs
        return MagicMock()
    
    mock_db.__getitem__ = mock_getitem
    
    # Mock the database import
    import database
    original_db = database.db
    database.db = mock_db
    
    try:
        user = {
            "id": "user-123",
            "email": "buyer@test.com",
            "company_id": "company-123"
        }
        
        # Call the endpoint
        result = await get_buyer_recent_rfqs(limit=10, user=user)
        
        # Verify response
        assert result["success"] is True
        assert result["rfqs"] == []
    finally:
        database.db = original_db


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

