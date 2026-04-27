"""
Test supplier stats API endpoint.
Tests GET /api/dashboard/supplier/stats endpoint.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.asyncio
async def test_get_supplier_stats_success(monkeypatch):
    """Test supplier stats endpoint returns correct data."""
    # Mock the static files directory before importing main
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_stats
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company lookup
        mock_db["companies"].find_one = AsyncMock(return_value={
            "id": "company-123",
            "unique_id": "SUP123456",
            "name": "Test Supplier",
            "role": "SUPPLIER"
        })
        
        # Mock active_bids count (ACTIVE or ACCEPTED)
        mock_db["bids"].count_documents = AsyncMock(side_effect=[
            5,  # active_bids (ACTIVE or ACCEPTED)
            20,  # total_bids
            8   # accepted_bids
        ])
        
        # Mock payments for expected_payouts
        async def mock_payments_find(query):
            payments = [
                {"amount": 1000.0},
                {"amount": 2500.0},
                {"amount": 1500.0}
            ]
            for payment in payments:
                yield payment
        
        mock_db["payments"].find = MagicMock(return_value=mock_payments_find({}))
        
        # Patch database
        import database
        monkeypatch.setattr(database, "db", mock_db)
        
        # Mock user
        user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        # Call endpoint
        result = await get_supplier_stats(user)
        
        # Verify response structure
        assert result["success"] is True
        assert "stats" in result
        
        stats = result["stats"]
        assert "active_bids" in stats
        assert "win_rate" in stats
        assert "expected_payouts" in stats
        
        # Verify calculations
        assert stats["active_bids"] == 5
        assert stats["win_rate"] == 40.0  # (8 / 20) * 100
        assert stats["expected_payouts"] == 5000.0  # 1000 + 2500 + 1500
        
        print("✓ Supplier stats endpoint returns correct data")


@pytest.mark.asyncio
async def test_get_supplier_stats_zero_bids(monkeypatch):
    """Test supplier stats endpoint handles zero bids case."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_stats
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company lookup
        mock_db["companies"].find_one = AsyncMock(return_value={
            "id": "company-123",
            "unique_id": "SUP123456",
            "name": "Test Supplier",
            "role": "SUPPLIER"
        })
        
        # Mock zero bids
        mock_db["bids"].count_documents = AsyncMock(side_effect=[
            0,  # active_bids
            0,  # total_bids
            0   # accepted_bids
        ])
        
        # Mock empty payments
        async def mock_payments_find(query):
            return
            yield  # Make it a generator
        
        mock_db["payments"].find = MagicMock(return_value=mock_payments_find({}))
        
        # Patch database
        import database
        monkeypatch.setattr(database, "db", mock_db)
        
        # Mock user
        user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        # Call endpoint
        result = await get_supplier_stats(user)
        
        # Verify response
        assert result["success"] is True
        stats = result["stats"]
        
        # Verify zero bids case
        assert stats["active_bids"] == 0
        assert stats["win_rate"] == 0.0  # Should be 0 when no bids
        assert stats["expected_payouts"] == 0.0
        
        print("✓ Supplier stats endpoint handles zero bids case")


@pytest.mark.asyncio
async def test_get_supplier_stats_company_not_found(monkeypatch):
    """Test supplier stats endpoint returns 404 when company not found."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_stats
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company not found
        mock_db["companies"].find_one = AsyncMock(return_value=None)
        
        # Patch database
        import database
        monkeypatch.setattr(database, "db", mock_db)
        
        # Mock user
        user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        # Call endpoint and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await get_supplier_stats(user)
        
        assert exc_info.value.status_code == 404
        assert "Company not found" in str(exc_info.value.detail)
        
        print("✓ Supplier stats endpoint returns 404 when company not found")


@pytest.mark.asyncio
async def test_get_supplier_stats_database_unavailable(monkeypatch):
    """Test supplier stats endpoint returns 500 when database unavailable."""
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_stats
        
        # Mock database as None
        import database
        monkeypatch.setattr(database, "db", None)
        
        # Mock user
        user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        # Call endpoint and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await get_supplier_stats(user)
        
        assert exc_info.value.status_code == 500
        assert "Database not available" in str(exc_info.value.detail)
        
        print("✓ Supplier stats endpoint returns 500 when database unavailable")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
