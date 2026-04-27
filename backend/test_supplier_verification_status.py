"""
Test supplier verification status API endpoint.
Tests GET /api/dashboard/supplier/verification-status endpoint.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.asyncio
async def test_get_supplier_verification_status_success():
    """Test verification status endpoint returns correct data."""
    # Mock the static files directory before importing main
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_verification_status
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company lookup
        mock_db["companies"].find_one = AsyncMock(return_value={
            "id": "company-123",
            "unique_id": "SUP123456",
            "name": "Test Supplier",
            "role": "SUPPLIER",
            "overall_status": "VERIFIED",
            "trust_score": 85
        })
        
        # Mock user
        mock_user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        # Patch database
        with patch('main.db', mock_db):
            # Call the endpoint function
            result = await get_supplier_verification_status(user=mock_user)
        
        # Verify response
        assert result["success"] is True
        assert "verification" in result
        
        verification = result["verification"]
        assert verification["status"] == "VERIFIED"
        assert verification["trust_score"] == 85
        assert verification["average_rating"] == 0.0  # No reviews system yet
        assert verification["total_reviews"] == 0  # No reviews system yet
        
        print("✅ Verification status endpoint test passed")


@pytest.mark.asyncio
async def test_get_supplier_verification_status_company_not_found():
    """Test verification status endpoint when company not found."""
    # Mock the static files directory before importing main
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_verification_status
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company lookup - return None (not found)
        mock_db["companies"].find_one = AsyncMock(return_value=None)
        
        # Mock user
        mock_user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        # Patch database
        with patch('main.db', mock_db):
            # Call the endpoint function - should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_supplier_verification_status(user=mock_user)
            
            assert exc_info.value.status_code == 404
            assert "Company not found" in exc_info.value.detail
        
        print("✅ Company not found test passed")


@pytest.mark.asyncio
async def test_get_supplier_verification_status_default_values():
    """Test verification status endpoint with default/missing values."""
    # Mock the static files directory before importing main
    with patch('fastapi.staticfiles.StaticFiles'):
        from main import get_supplier_verification_status
        
        # Mock database
        mock_db = MagicMock()
        
        # Mock company lookup with minimal data
        mock_db["companies"].find_one = AsyncMock(return_value={
            "id": "company-123",
            "unique_id": "SUP123456",
            "name": "Test Supplier",
            "role": "SUPPLIER"
            # Missing overall_status and trust_score
        })
        
        # Mock user
        mock_user = {
            "id": "user-123",
            "company_id": "company-123",
            "email": "supplier@test.com"
        }
        
        # Patch database
        with patch('main.db', mock_db):
            # Call the endpoint function
            result = await get_supplier_verification_status(user=mock_user)
        
        # Verify response with default values
        assert result["success"] is True
        verification = result["verification"]
        assert verification["status"] == "DRAFT"  # Default value
        assert verification["trust_score"] == 0  # Default value
        assert verification["average_rating"] == 0.0
        assert verification["total_reviews"] == 0
        
        print("✅ Default values test passed")


if __name__ == "__main__":
    import asyncio
    
    async def run_tests():
        try:
            await test_get_supplier_verification_status_success()
            await test_get_supplier_verification_status_company_not_found()
            await test_get_supplier_verification_status_default_values()
            print("\n✅ All tests passed!")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise
    
    asyncio.run(run_tests())

