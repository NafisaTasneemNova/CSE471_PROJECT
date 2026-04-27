"""
Test role-based authentication dependencies.
Tests require_buyer() and require_supplier() functions.
"""
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import require_buyer, require_supplier


@pytest.mark.asyncio
async def test_require_buyer_with_buyer_role(monkeypatch):
    """Test require_buyer allows access for users with BUYER role."""
    # Mock database
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value={
        "id": "company-123",
        "role": "BUYER",
        "name": "Test Buyer Company"
    })
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    
    # Mock the database import
    import database
    monkeypatch.setattr(database, "db", mock_db)
    
    # Test user with BUYER role
    user = {
        "id": "user-123",
        "email": "buyer@test.com",
        "company_id": "company-123"
    }
    
    result = await require_buyer(user)
    assert result == user


@pytest.mark.asyncio
async def test_require_buyer_with_supplier_role(monkeypatch):
    """Test require_buyer denies access for users with SUPPLIER role."""
    # Mock database
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value={
        "id": "company-456",
        "role": "SUPPLIER",
        "name": "Test Supplier Company"
    })
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    
    # Mock the database import
    import database
    monkeypatch.setattr(database, "db", mock_db)
    
    # Test user with SUPPLIER role
    user = {
        "id": "user-456",
        "email": "supplier@test.com",
        "company_id": "company-456"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        await require_buyer(user)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Buyer access required"


@pytest.mark.asyncio
async def test_require_supplier_with_supplier_role(monkeypatch):
    """Test require_supplier allows access for users with SUPPLIER role."""
    # Mock database
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value={
        "id": "company-456",
        "role": "SUPPLIER",
        "name": "Test Supplier Company"
    })
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    
    # Mock the database import
    import database
    monkeypatch.setattr(database, "db", mock_db)
    
    # Test user with SUPPLIER role
    user = {
        "id": "user-456",
        "email": "supplier@test.com",
        "company_id": "company-456"
    }
    
    result = await require_supplier(user)
    assert result == user


@pytest.mark.asyncio
async def test_require_supplier_with_buyer_role(monkeypatch):
    """Test require_supplier denies access for users with BUYER role."""
    # Mock database
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value={
        "id": "company-123",
        "role": "BUYER",
        "name": "Test Buyer Company"
    })
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    
    # Mock the database import
    import database
    monkeypatch.setattr(database, "db", mock_db)
    
    # Test user with BUYER role
    user = {
        "id": "user-123",
        "email": "buyer@test.com",
        "company_id": "company-123"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        await require_supplier(user)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Supplier access required"


@pytest.mark.asyncio
async def test_require_buyer_company_not_found(monkeypatch):
    """Test require_buyer returns 403 when company not found."""
    # Mock database
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    
    # Mock the database import
    import database
    monkeypatch.setattr(database, "db", mock_db)
    
    user = {
        "id": "user-999",
        "email": "test@test.com",
        "company_id": "nonexistent-company"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        await require_buyer(user)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Company not found"


@pytest.mark.asyncio
async def test_require_supplier_company_not_found(monkeypatch):
    """Test require_supplier returns 403 when company not found."""
    # Mock database
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    
    # Mock the database import
    import database
    monkeypatch.setattr(database, "db", mock_db)
    
    user = {
        "id": "user-999",
        "email": "test@test.com",
        "company_id": "nonexistent-company"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        await require_supplier(user)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Company not found"


@pytest.mark.asyncio
async def test_require_buyer_database_unavailable(monkeypatch):
    """Test require_buyer returns 500 when database is unavailable."""
    # Mock database as None
    import database
    monkeypatch.setattr(database, "db", None)
    
    user = {
        "id": "user-123",
        "email": "test@test.com",
        "company_id": "company-123"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        await require_buyer(user)
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Database not available"


@pytest.mark.asyncio
async def test_require_supplier_database_unavailable(monkeypatch):
    """Test require_supplier returns 500 when database is unavailable."""
    # Mock database as None
    import database
    monkeypatch.setattr(database, "db", None)
    
    user = {
        "id": "user-123",
        "email": "test@test.com",
        "company_id": "company-123"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        await require_supplier(user)
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Database not available"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
