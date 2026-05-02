"""
Test buyer action required API endpoint.
Tests GET /api/dashboard/buyer/action-required endpoint.
"""
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.asyncio
async def test_buyer_action_required_success():
    """Test buyer action required endpoint returns correct action items."""
    # Patch StaticFiles before importing main
    with patch('fastapi.staticfiles.StaticFiles'):
        # Import inside test to avoid static files issue
        from main import get_buyer_action_required
    
    # Mock database
    mock_db = MagicMock()
    
    # Mock payments collection
    mock_payments = AsyncMock()
    
    # Mock payment documents with SENT_FOR_DELIVERY status
    mock_payment_docs = [
        {
            "payment_id": "pay-1",
            "transaction_id": "TXN123456",
            "order_id": "rfq-1",
            "amount": 15000.0,
            "status": "SENT_FOR_DELIVERY"
        },
        {
            "payment_id": "pay-2",
            "transaction_id": "TXN789012",
            "order_id": "rfq-2",
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
        
        return MockCursor(mock_payment_docs)
    
    mock_payments.find = mock_find
    
    # Mock rfqs collection
    mock_rfqs = AsyncMock()
    
    async def mock_find_one(query):
        rfq_id = query.get("id")
        if rfq_id == "rfq-1":
            return {"id": "rfq-1", "title": "Cotton T-Shirts Order"}
        elif rfq_id == "rfq-2":
            return {"id": "rfq-2", "title": "Denim Jeans Order"}
        return None
    
    mock_rfqs.find_one = mock_find_one
    
    # Setup mock_db to return appropriate collections
    def mock_getitem(self, key):
        if key == "payments":
            return mock_payments
        elif key == "rfqs":
            return mock_rfqs
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
        result = await get_buyer_action_required(user)
        
        # Verify response structure
        assert result["success"] is True
        assert "actions" in result
        
        # Verify actions
        actions = result["actions"]
        assert len(actions) == 2
        
        # Verify first action
        assert actions[0]["payment_id"] == "pay-1"
        assert actions[0]["transaction_id"] == "TXN123456"
        assert actions[0]["action"] == "confirm_delivery"
        assert actions[0]["description"] == "Supplier has marked order as delivered. Please confirm receipt."
        assert actions[0]["amount"] == 15000.0
        assert actions[0]["rfq_title"] == "Cotton T-Shirts Order"
        
        # Verify second action
        assert actions[1]["payment_id"] == "pay-2"
        assert actions[1]["transaction_id"] == "TXN789012"
        assert actions[1]["action"] == "confirm_delivery"
        assert actions[1]["amount"] == 25000.0
        assert actions[1]["rfq_title"] == "Denim Jeans Order"
    finally:
        database.db = original_db


@pytest.mark.asyncio
async def test_buyer_action_required_database_unavailable():
    """Test buyer action required endpoint returns 500 when database is unavailable."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_buyer_action_required
    
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
            await get_buyer_action_required(user)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Database not available"
    finally:
        database.db = original_db


@pytest.mark.asyncio
async def test_buyer_action_required_no_actions():
    """Test buyer action required endpoint with no pending actions."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_buyer_action_required
    
    # Mock database
    mock_db = MagicMock()
    
    # Mock payments collection - no payments with SENT_FOR_DELIVERY status
    mock_payments = AsyncMock()
    
    def mock_find(*args, **kwargs):
        class MockCursor:
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                raise StopAsyncIteration
        
        return MockCursor()
    
    mock_payments.find = mock_find
    
    # Setup mock_db
    def mock_getitem(self, key):
        if key == "payments":
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
        
        # Call the endpoint
        result = await get_buyer_action_required(user)
        
        # Verify response
        assert result["success"] is True
        assert result["actions"] == []
    finally:
        database.db = original_db


@pytest.mark.asyncio
async def test_buyer_action_required_missing_rfq():
    """Test buyer action required endpoint handles missing RFQ gracefully."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_buyer_action_required
    
    # Mock database
    mock_db = MagicMock()
    
    # Mock payments collection
    mock_payments = AsyncMock()
    
    mock_payment_docs = [
        {
            "payment_id": "pay-1",
            "transaction_id": "TXN123456",
            "order_id": "rfq-nonexistent",
            "amount": 15000.0,
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
        
        return MockCursor(mock_payment_docs)
    
    mock_payments.find = mock_find
    
    # Mock rfqs collection - returns None for missing RFQ
    mock_rfqs = AsyncMock()
    mock_rfqs.find_one = AsyncMock(return_value=None)
    
    # Setup mock_db
    def mock_getitem(self, key):
        if key == "payments":
            return mock_payments
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
        result = await get_buyer_action_required(user)
        
        # Verify response
        assert result["success"] is True
        assert len(result["actions"]) == 1
        
        # Verify action has "Unknown RFQ" as title
        assert result["actions"][0]["rfq_title"] == "Unknown RFQ"
        assert result["actions"][0]["payment_id"] == "pay-1"
    finally:
        database.db = original_db


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
