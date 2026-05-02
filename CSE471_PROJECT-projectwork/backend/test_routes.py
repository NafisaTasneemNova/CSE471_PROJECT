#!/usr/bin/env python3
"""
Test script to verify all dashboard routes are properly registered.
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_routes():
    """Test that all required routes are registered."""
    try:
        # Import without static files issues
        import importlib.util
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        spec = importlib.util.spec_from_file_location("main", main_path)
        main_module = importlib.util.module_from_spec(spec)
        
        # Mock StaticFiles to avoid directory issues
        import unittest.mock
        with unittest.mock.patch('fastapi.staticfiles.StaticFiles'):
            spec.loader.exec_module(main_module)
            app = main_module.app
        
        print('✓ FastAPI app imports successfully')
        
        # Check if all required endpoints exist
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        
        required_routes = [
            '/dashboard',
            '/dashboard/buyer', 
            '/dashboard/supplier',
            '/api/dashboard/buyer/stats',
            '/api/dashboard/buyer/recent-rfqs',
            '/api/dashboard/buyer/action-required',
            '/api/dashboard/supplier/stats',
            '/api/dashboard/supplier/open-rfqs',
            '/api/dashboard/supplier/verification-status',
            '/api/dashboard/supplier/active-production'
        ]
        
        missing_routes = []
        existing_routes = []
        
        for route in required_routes:
            if route not in routes:
                missing_routes.append(route)
            else:
                existing_routes.append(route)
        
        print(f'✓ Found {len(existing_routes)} required routes:')
        for route in existing_routes:
            print(f'  - {route}')
        
        if missing_routes:
            print(f'✗ Missing routes: {missing_routes}')
            return False
        else:
            print('✓ All required routes are registered')
            return True
            
    except Exception as e:
        print(f'✗ Error importing app: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_routes()
    sys.exit(0 if success else 1)