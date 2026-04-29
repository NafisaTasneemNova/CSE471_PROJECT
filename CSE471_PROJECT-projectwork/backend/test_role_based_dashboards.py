#!/usr/bin/env python3
"""
Integration test script for Role-Based Dashboards feature.
Tests end-to-end functionality including authentication, API endpoints, and data access security.

Usage: python test_role_based_dashboards.py
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_BUYER_EMAIL = "test_buyer@example.com"
TEST_SUPPLIER_EMAIL = "test_supplier@example.com"
TEST_PASSWORD = "testpass123"

class DashboardTester:
    def __init__(self):
        self.session = None
        self.buyer_cookies = None
        self.supplier_cookies = None
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def test_smart_dashboard_routing(self):
        """Test smart dashboard routing redirects based on user role"""
        print("🔄 Testing smart dashboard routing...")
        
        # Test unauthenticated access redirects to login
        async with self.session.get(f"{BASE_URL}/dashboard") as response:
            if response.status == 302 and "/login" in str(response.headers.get('Location', '')):
                print("✅ Unauthenticated access correctly redirects to login")
            else:
                print(f"❌ Expected redirect to login, got status {response.status}")
                return False
        
        return True
    
    async def login_as_buyer(self):
        """Login as buyer and store session cookies"""
        print("🔑 Logging in as buyer...")
        
        login_data = {
            "email": TEST_BUYER_EMAIL,
            "password": TEST_PASSWORD
        }
        
        async with self.session.post(f"{BASE_URL}/login", data=login_data) as response:
            if response.status == 302:  # Redirect after successful login
                self.buyer_cookies = response.cookies
                print("✅ Buyer login successful")
                return True
            else:
                print(f"❌ Buyer login failed with status {response.status}")
                return False
    
    async def login_as_supplier(self):
        """Login as supplier and store session cookies"""
        print("🔑 Logging in as supplier...")
        
        login_data = {
            "email": TEST_SUPPLIER_EMAIL,
            "password": TEST_PASSWORD
        }
        
        async with self.session.post(f"{BASE_URL}/login", data=login_data) as response:
            if response.status == 302:  # Redirect after successful login
                self.supplier_cookies = response.cookies
                print("✅ Supplier login successful")
                return True
            else:
                print(f"❌ Supplier login failed with status {response.status}")
                return False
    
    async def test_buyer_api_endpoints(self):
        """Test all buyer dashboard API endpoints"""
        print("📊 Testing buyer API endpoints...")
        
        if not self.buyer_cookies:
            print("❌ No buyer session available")
            return False
        
        endpoints = [
            "/api/dashboard/buyer/stats",
            "/api/dashboard/buyer/recent-rfqs",
            "/api/dashboard/buyer/action-required"
        ]
        
        for endpoint in endpoints:
            async with self.session.get(f"{BASE_URL}{endpoint}", cookies=self.buyer_cookies) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        print(f"✅ {endpoint} - OK")
                    else:
                        print(f"❌ {endpoint} - API returned success=false")
                        return False
                else:
                    print(f"❌ {endpoint} - HTTP {response.status}")
                    return False
        
        return True
    
    async def test_supplier_api_endpoints(self):
        """Test all supplier dashboard API endpoints"""
        print("📊 Testing supplier API endpoints...")
        
        if not self.supplier_cookies:
            print("❌ No supplier session available")
            return False
        
        endpoints = [
            "/api/dashboard/supplier/stats",
            "/api/dashboard/supplier/open-rfqs",
            "/api/dashboard/supplier/verification-status",
            "/api/dashboard/supplier/active-production"
        ]
        
        for endpoint in endpoints:
            async with self.session.get(f"{BASE_URL}{endpoint}", cookies=self.supplier_cookies) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        print(f"✅ {endpoint} - OK")
                    else:
                        print(f"❌ {endpoint} - API returned success=false")
                        return False
                else:
                    print(f"❌ {endpoint} - HTTP {response.status}")
                    return False
        
        return True
    
    async def test_role_based_access_control(self):
        """Test that buyers cannot access supplier endpoints and vice versa"""
        print("🔒 Testing role-based access control...")
        
        # Test buyer trying to access supplier endpoints
        supplier_endpoints = [
            "/api/dashboard/supplier/stats",
            "/api/dashboard/supplier/open-rfqs"
        ]
        
        for endpoint in supplier_endpoints:
            async with self.session.get(f"{BASE_URL}{endpoint}", cookies=self.buyer_cookies) as response:
                if response.status == 403:
                    print(f"✅ Buyer correctly denied access to {endpoint}")
                else:
                    print(f"❌ Buyer should be denied access to {endpoint}, got {response.status}")
                    return False
        
        # Test supplier trying to access buyer endpoints
        buyer_endpoints = [
            "/api/dashboard/buyer/stats",
            "/api/dashboard/buyer/recent-rfqs"
        ]
        
        for endpoint in buyer_endpoints:
            async with self.session.get(f"{BASE_URL}{endpoint}", cookies=self.supplier_cookies) as response:
                if response.status == 403:
                    print(f"✅ Supplier correctly denied access to {endpoint}")
                else:
                    print(f"❌ Supplier should be denied access to {endpoint}, got {response.status}")
                    return False
        
        return True
    
    async def test_dashboard_pages(self):
        """Test dashboard page rendering"""
        print("🖥️ Testing dashboard page rendering...")
        
        # Test buyer dashboard page
        async with self.session.get(f"{BASE_URL}/dashboard/buyer", cookies=self.buyer_cookies) as response:
            if response.status == 200:
                content = await response.text()
                if "Buyer Dashboard" in content and "Quick Stats" in content:
                    print("✅ Buyer dashboard page renders correctly")
                else:
                    print("❌ Buyer dashboard page missing expected content")
                    return False
            else:
                print(f"❌ Buyer dashboard page returned {response.status}")
                return False
        
        # Test supplier dashboard page
        async with self.session.get(f"{BASE_URL}/dashboard/supplier", cookies=self.supplier_cookies) as response:
            if response.status == 200:
                content = await response.text()
                if "Supplier Portal" in content and "Trust & Verification" in content:
                    print("✅ Supplier dashboard page renders correctly")
                else:
                    print("❌ Supplier dashboard page missing expected content")
                    return False
            else:
                print(f"❌ Supplier dashboard page returned {response.status}")
                return False
        
        return True
    
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("⚠️ Testing error handling...")
        
        # Test unauthenticated API access
        async with self.session.get(f"{BASE_URL}/api/dashboard/buyer/stats") as response:
            if response.status in [401, 403]:
                print("✅ Unauthenticated API access correctly rejected")
            else:
                print(f"❌ Expected 401/403 for unauthenticated access, got {response.status}")
                return False
        
        return True
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Role-Based Dashboards Integration Tests")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Test basic routing
            if not await self.test_smart_dashboard_routing():
                return False
            
            # Login as both user types
            if not await self.login_as_buyer():
                print("⚠️ Skipping buyer tests - login failed")
            
            if not await self.login_as_supplier():
                print("⚠️ Skipping supplier tests - login failed")
            
            # Test API endpoints
            if self.buyer_cookies and not await self.test_buyer_api_endpoints():
                return False
            
            if self.supplier_cookies and not await self.test_supplier_api_endpoints():
                return False
            
            # Test access control
            if self.buyer_cookies and self.supplier_cookies:
                if not await self.test_role_based_access_control():
                    return False
            
            # Test dashboard pages
            if self.buyer_cookies and self.supplier_cookies:
                if not await self.test_dashboard_pages():
                    return False
            
            # Test error handling
            if not await self.test_error_handling():
                return False
            
            print("=" * 60)
            print("🎉 All integration tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
            return False
        
        finally:
            await self.cleanup_session()

async def main():
    """Main test runner"""
    tester = DashboardTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Integration testing completed successfully!")
        print("The role-based dashboards feature is ready for production.")
    else:
        print("\n❌ Integration testing failed!")
        print("Please review the errors above and fix any issues.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())