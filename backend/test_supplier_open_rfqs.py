"""
Test supplier open RFQs API endpoint.
Tests GET /api/dashboard/supplier/open-rfqs endpoint.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.asyncio
async def test_get_open_rfqs_success(monkeypatch):
    """Test successful retrieval of open RFQs."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_open_rfqs
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company lookup
        mock_db["companies"].find_one = AsyncMock(return_value={
            "id": "company-123",
            "unique_id": "SUP123456",
            "name": "Test Supplier",
            "role": "SUPPLIER"
        })
        
        # Mock RFQs
        test_rfqs = [
            {
                "_id": "obj1",
                "id": "rfq-1",
                "title": "Cotton T-Shirts Order",
                "product_category": "T-Shirts",
                "quantity": 5000,
                "urgency_level": "HIGH",
                "status": "OPEN",
                "target_delivery_date": datetime.utcnow() + timedelta(days=30),
                "created_at": datetime.utcnow() - timedelta(days=1),
            },
            {
                "_id": "obj2",
                "id": "rfq-2",
                "title": "Denim Jeans Order",
                "product_category": "Denim",
                "quantity": 3000,
                "urgency_level": "MEDIUM",
                "status": "OPEN",
                "target_delivery_date": datetime.utcnow() + timedelta(days=45),
                "created_at": datetime.utcnow() - timedelta(days=2),
            },
            {
                "_id": "obj3",
                "id": "rfq-3",
                "title": "Activewear Order",
                "product_category": "Activewear",
                "quantity": 2000,
                "urgency_level": "LOW",
                "status": "OPEN",
                "target_delivery_date": datetime.utcnow() + timedelta(days=60),
                "created_at": datetime.utcnow() - timedelta(days=3),
            }
        ]
        
        async def mock_rfqs_find(query):
            for rfq in test_rfqs:
                yield rfq
        
        mock_find = MagicMock()
        mock_find.sort = MagicMock(return_value=mock_find)
        mock_find.limit = MagicMock(return_value=mock_rfqs_find({}))
        mock_db["rfqs"].find = MagicMock(return_value=mock_find)
        
        # Patch database
        import database
        monkeypatch.setattr(database, "db", mock_db)
        
        # Mock user
        mock_user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        result = await get_supplier_open_rfqs(user=mock_user, limit=20, category=None, urgency=None)
        
        assert result["success"] is True
        assert "rfqs" in result
        assert len(result["rfqs"]) == 3
        
        # Verify required fields are present
        for rfq in result["rfqs"]:
            assert "id" in rfq
            assert "title" in rfq
            assert "product_category" in rfq
            assert "quantity" in rfq
            assert "urgency_level" in rfq
            assert "target_delivery_date" in rfq
            assert "created_at" in rfq


@pytest.mark.asyncio
async def test_get_open_rfqs_with_category_filter(monkeypatch):
    """Test filtering RFQs by category."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_open_rfqs
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company lookup
        mock_db["companies"].find_one = AsyncMock(return_value={
            "id": "company-123",
            "unique_id": "SUP123456",
            "name": "Test Supplier",
            "role": "SUPPLIER"
        })
        
        # Mock RFQs - only T-Shirts category
        test_rfqs = [
            {
                "_id": "obj1",
                "id": "rfq-1",
                "title": "Cotton T-Shirts Order",
                "product_category": "T-Shirts",
                "quantity": 5000,
                "urgency_level": "HIGH",
                "status": "OPEN",
                "target_delivery_date": datetime.utcnow() + timedelta(days=30),
                "created_at": datetime.utcnow() - timedelta(days=1),
            }
        ]
        
        async def mock_rfqs_find(query):
            # Verify category filter is applied
            assert query.get("product_category") == "T-Shirts"
            for rfq in test_rfqs:
                yield rfq
        
        mock_find = MagicMock()
        mock_find.sort = MagicMock(return_value=mock_find)
        mock_find.limit = MagicMock(return_value=mock_rfqs_find({"product_category": "T-Shirts"}))
        mock_db["rfqs"].find = MagicMock(return_value=mock_find)
        
        # Patch database
        import database
        monkeypatch.setattr(database, "db", mock_db)
        
        # Mock user
        mock_user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        result = await get_supplier_open_rfqs(user=mock_user, limit=20, category="T-Shirts", urgency=None)
        
        assert result["success"] is True
        assert len(result["rfqs"]) == 1
        assert result["rfqs"][0]["product_category"] == "T-Shirts"


@pytest.mark.asyncio
async def test_get_open_rfqs_with_urgency_filter(monkeypatch):
    """Test filtering RFQs by urgency level."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_open_rfqs
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company lookup
        mock_db["companies"].find_one = AsyncMock(return_value={
            "id": "company-123",
            "unique_id": "SUP123456",
            "name": "Test Supplier",
            "role": "SUPPLIER"
        })
        
        # Mock RFQs - only HIGH urgency
        test_rfqs = [
            {
                "_id": "obj1",
                "id": "rfq-1",
                "title": "Cotton T-Shirts Order",
                "product_category": "T-Shirts",
                "quantity": 5000,
                "urgency_level": "HIGH",
                "status": "OPEN",
                "target_delivery_date": datetime.utcnow() + timedelta(days=30),
                "created_at": datetime.utcnow() - timedelta(days=1),
            }
        ]
        
        async def mock_rfqs_find(query):
            # Verify urgency filter is applied
            assert query.get("urgency_level") == "HIGH"
            for rfq in test_rfqs:
                yield rfq
        
        mock_find = MagicMock()
        mock_find.sort = MagicMock(return_value=mock_find)
        mock_find.limit = MagicMock(return_value=mock_rfqs_find({"urgency_level": "HIGH"}))
        mock_db["rfqs"].find = MagicMock(return_value=mock_find)
        
        # Patch database
        import database
        monkeypatch.setattr(database, "db", mock_db)
        
        # Mock user
        mock_user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        result = await get_supplier_open_rfqs(user=mock_user, limit=20, category=None, urgency="HIGH")
        
        assert result["success"] is True
        assert len(result["rfqs"]) == 1
        assert result["rfqs"][0]["urgency_level"] == "HIGH"


@pytest.mark.asyncio
async def test_get_open_rfqs_with_limit(monkeypatch):
    """Test limiting the number of RFQs returned."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_open_rfqs
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company lookup
        mock_db["companies"].find_one = AsyncMock(return_value={
            "id": "company-123",
            "unique_id": "SUP123456",
            "name": "Test Supplier",
            "role": "SUPPLIER"
        })
        
        # Mock RFQs - only 2 returned due to limit
        test_rfqs = [
            {
                "_id": "obj1",
                "id": "rfq-1",
                "title": "Cotton T-Shirts Order",
                "product_category": "T-Shirts",
                "quantity": 5000,
                "urgency_level": "HIGH",
                "status": "OPEN",
                "target_delivery_date": datetime.utcnow() + timedelta(days=30),
                "created_at": datetime.utcnow() - timedelta(days=1),
            },
            {
                "_id": "obj2",
                "id": "rfq-2",
                "title": "Denim Jeans Order",
                "product_category": "Denim",
                "quantity": 3000,
                "urgency_level": "MEDIUM",
                "status": "OPEN",
                "target_delivery_date": datetime.utcnow() + timedelta(days=45),
                "created_at": datetime.utcnow() - timedelta(days=2),
            }
        ]
        
        async def mock_rfqs_find(query):
            for rfq in test_rfqs:
                yield rfq
        
        mock_find = MagicMock()
        mock_find.sort = MagicMock(return_value=mock_find)
        mock_find.limit = MagicMock(return_value=mock_rfqs_find({}))
        mock_db["rfqs"].find = MagicMock(return_value=mock_find)
        
        # Patch database
        import database
        monkeypatch.setattr(database, "db", mock_db)
        
        # Mock user
        mock_user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        result = await get_supplier_open_rfqs(user=mock_user, limit=2, category=None, urgency=None)
        
        assert result["success"] is True
        assert len(result["rfqs"]) == 2


@pytest.mark.asyncio
async def test_get_open_rfqs_database_unavailable():
    """Test error handling when database is unavailable."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_open_rfqs
        
        # Mock user
        mock_user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        # Patch database to None
        with patch('main.db', None):
            with pytest.raises(HTTPException) as exc_info:
                await get_supplier_open_rfqs(user=mock_user, limit=20, category=None, urgency=None)
            
            assert exc_info.value.status_code == 500
            assert "Database not available" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_open_rfqs_empty_results(monkeypatch):
    """Test endpoint returns empty list when no RFQs match filters."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_open_rfqs
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company lookup
        mock_db["companies"].find_one = AsyncMock(return_value={
            "id": "company-123",
            "unique_id": "SUP123456",
            "name": "Test Supplier",
            "role": "SUPPLIER"
        })
        
        # Mock empty RFQs
        async def mock_rfqs_find(query):
            return
            yield  # Make it a generator
        
        mock_find = MagicMock()
        mock_find.sort = MagicMock(return_value=mock_find)
        mock_find.limit = MagicMock(return_value=mock_rfqs_find({}))
        mock_db["rfqs"].find = MagicMock(return_value=mock_find)
        
        # Patch database
        import database
        monkeypatch.setattr(database, "db", mock_db)
        
        # Mock user
        mock_user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        result = await get_supplier_open_rfqs(user=mock_user, limit=20, category=None, urgency=None)
        
        assert result["success"] is True
        assert len(result["rfqs"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
