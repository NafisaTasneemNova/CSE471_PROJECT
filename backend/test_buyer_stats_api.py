"""
Test buyer stats API endpoint.
Tests GET /api/dashboard/buyer/stats endpoint.
"""
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.asyncio
async def test_buyer_stats_success():
    """Test buyer stats endpoint returns correct statistics."""
    # Import inside test to avoid static files issue
    with patch('main.StaticFiles'):
        from main import get_buyer_stats
    
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
    
    # Mock rfqs collection
    mock_rfqs = AsyncMock()
    
    # Mock count_documents calls for different queries
    async def mock_count_documents(query):
        # Active RFQs (OPEN or EVALUATING)
        if "status" in query and "$in" in query["status"]:
            if set(query["status"]["$in"]) == {"OPEN", "EVALUATING"}:
                return 5
            # Completed orders (AWARDED or CLOSED)
            elif set(query["status"]["$in"]) == {"AWARDED", "CLOSED"}:
                return 3
        return 0
    
    mock_rfqs.count_documents = mock_count_documents
    
    # Mock payments collection
    mock_payments = AsyncMock()
    
    # Mock payments cursor for funds in escrow
    mock_payment_docs = [
        {"payment_id": "pay-1", "amount": 10000.0, "status": "PAID_IN_ESCROW"},
        {"payment_id": "pay-2", "amount": 15000.0, "status": "WORK_IN_PROGRESS"},
        {"payment_id": "pay-3", "amount": 20000.0, "status": "PAID_IN_ESCROW"}
    ]
    
    async def mock_find(*args, **kwargs):
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
    
    # Setup mock_db to return appropriate collections
    def mock_getitem(key):
        if key == "companies":
            return mock_companies
        elif key == "rfqs":
            return mock_rfqs
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
        result = await get_buyer_stats(user)
        
        # Verify response structure
        assert result["success"] is True
        assert "stats" in result
        
        # Verify stats values
        stats = result["stats"]
        assert stats["active_rfqs"] == 5
        assert stats["funds_in_escrow"] == 45000.0  # 10000 + 15000 + 20000
        assert stats["completed_orders"] == 3
    finally:
        database.db = original_db


@pytest.mark.asyncio
async def test_buyer_stats_database_unavailable():
    """Test buyer stats endpoint returns 500 when database is unavailable."""
    with patch('main.StaticFiles'):
        from main import get_buyer_stats
    
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
            await get_buyer_stats(user)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Database not available"
    finally:
        database.db = original_db


@pytest.mark.asyncio
async def test_buyer_stats_company_not_found():
    """Test buyer stats endpoint returns 404 when company not found."""
    with patch('main.StaticFiles'):
        from main import get_buyer_stats
    
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
            await get_buyer_stats(user)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Company not found"
    finally:
        database.db = original_db


@pytest.mark.asyncio
async def test_buyer_stats_empty_data():
    """Test buyer stats endpoint with no RFQs or payments."""
    with patch('main.StaticFiles'):
        from main import get_buyer_stats
    
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
    mock_rfqs.count_documents = AsyncMock(return_value=0)
    
    # Mock payments collection - no payments
    mock_payments = AsyncMock()
    
    async def mock_find(*args, **kwargs):
        class MockCursor:
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                raise StopAsyncIteration
        
        return MockCursor()
    
    mock_payments.find = mock_find
    
    # Setup mock_db
    def mock_getitem(key):
        if key == "companies":
            return mock_companies
        elif key == "rfqs":
            return mock_rfqs
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
        
        # Call the endpoint
        result = await get_buyer_stats(user)
        
        # Verify response
        assert result["success"] is True
        assert result["stats"]["active_rfqs"] == 0
        assert result["stats"]["funds_in_escrow"] == 0.0
        assert result["stats"]["completed_orders"] == 0
    finally:
        database.db = original_db


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
